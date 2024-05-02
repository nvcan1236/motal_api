from datetime import datetime

from rest_framework import viewsets, generics, response, status, permissions
from rest_framework.decorators import action

from motel import serializers, perms
from motel.models import User, Follow, Motel, MotelImage, Price, Reservation
from motel.serializers import PriceSerializer, ImageSerializer


class UpdatePartialAPIView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        # Chỉ cho phép PATCH
        if not request.method == 'PATCH':
            return response.Response({"message": "Only PATCH method is allowed"},
                                     status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return response.Response(serializer.data)


class DestroySoftAPIView(generics.DestroyAPIView):
    def destroy(self, request, *args, **kwargs):
        image = self.get_object()
        image.is_active = False
        image.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.DetailUserSerializer
    queryset = User.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['get_followers', 'get_following', 'follow', 'current_user', 'get_motels']:
            return [permissions.IsAuthenticated()]

        if self.action in ['update', 'partial_update']:
            return [perms.IsOwner()]

        return [permissions.AllowAny()]

    @action(methods=['get', 'patch', 'delete'], url_path='current_user', detail=False)
    def current_user(self, request):
        if request.method.__eq__('DELETE'):
            user = request.user
            user.is_active = False
            user.save()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method.__eq__("PATCH"):
            user = request.user
            for key, value in request.data.items():
                setattr(user, key, value)
            user.save()

        return response.Response(serializers.DetailUserSerializer(request.user).data)

    @action(methods=['get'], url_path='followers', detail=True)
    def get_followers(self, request, pk):
        followers = Follow.objects.filter(following=self.get_object(), is_active=True).all()
        serializer = serializers.UserSerializer([follow.follower for follow in followers], many=True)

        return response.Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['get'], url_path='following', detail=True)
    def get_following(self, request, pk):
        following = Follow.objects.filter(follower=self.get_object(), is_active=True).all()
        serializer = serializers.UserSerializer([follow.following for follow in following], many=True)
        return response.Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['get'], url_path='motels', detail=True)
    def get_motels(self, request, pk):
        if request.user.__eq__(self.get_object()):
            motels = Motel.objects.filter(owner=self.get_object(), is_active=True).all()
        else:
            motels = Motel.objects.filter(owner=self.get_object(), is_active=True, approved=True).all()

        return response.Response(serializers.MotelSerializer(motels, many=True).data, status.HTTP_200_OK)

    @action(methods=['post'], url_path='follow', detail=True)
    def follow(self, request, pk):

        f, created = Follow.objects.get_or_create(follower=request.user, following=self.get_object())

        if not created:
            f.is_active = not f.is_active
            f.save()

        return response.Response(status=status.HTTP_200_OK)


class MotelViewSet(viewsets.ViewSet, UpdatePartialAPIView, generics.CreateAPIView, generics.RetrieveDestroyAPIView):
    def get_permissions(self):
        if self.action in ['partial_update', 'images', 'destroy', 'prices']:
            return [perms.MotelOwnerAuthenticated()]

        if self.action in ['create', ]:
            return [perms.IsMotelOwner()]

        if self.action in ['get_reservation', 'reserve']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='images')
    def images(self, request, pk):
        if request.method.__eq__('POST'):
            images = request.FILES.getlist('images')
            uploaded_images = []
            for image in images:
                i = MotelImage.objects.create(url=image, motel=self.get_object())
                uploaded_images.append(i)

            return response.Response(serializers.ImageSerializer(uploaded_images, many=True).data,
                                     status=status.HTTP_200_OK)

        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post'], url_path='prices', detail=True)
    def prices(self, request, pk):
        if request.method.__eq__('POST'):
            price_data = request.data.copy()
            price_data['motel'] = self.get_object().id
            serializer = PriceSerializer(data=price_data)

            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(url_path='reservations', methods=['get'], detail=False)
    def get_reservation(self, request):
        reservations = Reservation.objects.filter(user=request.user, is_active=True)
        return response.Response(serializers.ReservationSerializer(reservations, many=True).data, status.HTTP_200_OK)

    @action(url_path='reserve', methods=['post'], detail=True)
    def reserve(self, request, pk):
        motel = self.get_object()
        reserved = Reservation.objects.filter(is_active=True, motel=motel,
                                              expiration__gt=datetime.now()).first()

        if reserved:
            if reserved.user.__eq__(request.user):
                reserved.is_active = False
                reserved.save()
                return response.Response({"message": "Đã huỷ đặt trước"}, status.HTTP_204_NO_CONTENT)
            return response.Response({"message": "Trọ đã được đặt trước"}, status.HTTP_400_BAD_REQUEST)

        reservation = Reservation.objects.create(user=request.user, motel=motel)
        return response.Response(serializers.ReservationSerializer(reservation).data, status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        motel = self.get_object()
        motel.is_active = False
        motel.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    serializer_class = serializers.DetailMotelSerializer
    queryset = Motel.objects.filter(is_active=True, approved=True).all()


class ImageViewSet(viewsets.ViewSet, DestroySoftAPIView):
    serializer_class = ImageSerializer
    queryset = MotelImage.objects.filter(is_active=True).all()
    permission_classes = [perms.HasMotelOwnerAuthenticated]


class PriceViewSet(viewsets.ViewSet, DestroySoftAPIView, UpdatePartialAPIView):
    serializer_class = PriceSerializer
    queryset = Price.objects.filter(is_active=True).all()
    permission_classes = [perms.HasMotelOwnerAuthenticated]
