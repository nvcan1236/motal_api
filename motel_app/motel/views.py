from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, response, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.views import APIView
import vnpay

from motel import serializers, perms, paginators
from motel.models import User, Follow, Motel, MotelImage, Price, Reservation, UserRole
from vnpay.models import Billing
from motel.utils import send_motel_news_email
from post.models import PostForRent, PostForLease
from post.serializers import ReadPostForRentSerializer, ReadPostForLeaseSerializer
from motel.serializers import PriceSerializer, ImageSerializer, WriteMotelSerializer


# class VNPayCheckoutAPI(APIView):
#     def post(self, request, *args, **kwargs):
#         # Get necessary data from request
#         amount = request.data.get('amount')
#         order_info = request.data.get('order_info')
#
#         # Generate VNPay payment data
#         payment_data = vnpay.create_payment_data(amount=amount, order_info=order_info)
#         bill = Billing.objects.get(payment_data)
#         # In a real-world application, you might want to save payment_data in your database
#         # and return a unique identifier or token for this transaction
#
#
#         return response.Response(payment_data)


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
        if self.action in ['get_followers', 'get_following', 'follow', 'current_user', 'get_motels', 'get_posts']:
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

        return response.Response(serializers.DetailOwnerMotelSerializer(motels, many=True).data, status.HTTP_200_OK)

    @action(methods=['post'], url_path='follow', detail=True)
    def follow(self, request, pk):

        f, created = Follow.objects.get_or_create(follower=request.user, following=self.get_object())

        if not created:
            f.is_active = not f.is_active
            f.save()

        return response.Response(status=status.HTTP_200_OK)

    @action(url_path='post', methods=['get'], detail=True)
    def get_posts(self, request, pk):
        user = self.get_object()

        if user.user_role.__eq__(UserRole.TENANT):
            post = PostForRent.objects.filter(user=user, is_active=True)
            return response.Response(
                ReadPostForRentSerializer(post, many=True, context={'request': request}).data, status.HTTP_200_OK)
        elif user.user_role.__eq__(UserRole.MOTEL_OWNER):
            post = PostForLease.objects.filter(user=user, is_active=True)
            return response.Response(
                ReadPostForLeaseSerializer(post, many=True, context={'request': request}).data, status.HTTP_200_OK)


class MotelViewSet(viewsets.ViewSet,
                   UpdatePartialAPIView,
                   generics.ListCreateAPIView,
                   generics.RetrieveDestroyAPIView):
    pagination_class = paginators.MotelPaginator
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['price', 'ward', 'district', 'city', 'other_address', 'description']
    filterset_fields = ['price', 'ward', 'district', 'city', 'other_address', 'area']
    ordering_fields = ['price', 'area']
    ordering = ['price']

    def get_permissions(self):
        if self.action in ['partial_update', 'images', 'destroy', 'prices']:
            return [perms.MotelOwnerAuthenticated()]

        if self.action in ['create', ]:
            return [perms.IsMotelOwner()]

        if self.action in ['get_reservation', 'reserve']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action.__eq__('list'):
            return serializers.MotelSerializer
        return serializers.DetailMotelSerializer

    def get_queryset(self):
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        min_area = self.request.query_params.get('min_area', None)
        max_area = self.request.query_params.get('max_area', None)
        lat = self.request.query_params.get('lat', None)
        lon = self.request.query_params.get('lon', None)

        if self.action in ['partial_update', 'images', 'destroy', 'prices']:
            queryset = Motel.objects.filter(is_active=True)
        else:
            queryset = Motel.objects.filter(is_active=True, approved=True)

        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price))
        elif min_price:
            queryset = queryset.filter(price__gte=min_price)
        elif max_price:
            queryset = queryset.filter(price__lte=max_price)

        if min_area and max_area:
            queryset = queryset.filter(area__range=(min_area, max_area))
        elif min_area:
            queryset = queryset.filter(area__gte=min_area)
        elif max_area:
            queryset = queryset.filter(area__lte=max_area)

        if lat and lon:
            lat = float(lat)
            lon = float(lon)
            queryset = queryset.filter(lat__range=(lat - 0.03, lat + 0.03), lon__range=(lon - 0.03, lon + 0.03))

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = WriteMotelSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            context = {
                'user': self.request.user,
                'motel': serializer.data
            }
            send_motel_news_email(context)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(status=status.HTTP_400_BAD_REQUEST)

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

    @action(url_path='reserve', methods=['post'], detail=True)
    def reserve(self, request, pk):
        motel = self.get_object()
        bill = Billing.objects.get(reference_number=request.data.get("vnp_TransactionNo"))
        if bill:
            bill.result_payment = request.data.get("vnp_TransactionStatus")
            bill.is_paid = request.data.get("vnp_TransactionStatus") == "00"
            bill.transaction_id = request.data.get("vnp_TransactionNo")
            pay_at_str = request.data.get("vnp_PayDate")
            bill.pay_at = datetime.strptime(pay_at_str, '%Y%m%d%H%M%S')
            bill.save()

            reservation = Reservation.objects.create(user=request.user, motel=motel)
            return response.Response(serializers.ReservationSerializer(reservation).data, status.HTTP_201_CREATED)
        else:
            return response.Response({"Message": "Thông tin thanh toán không hợp lệ!!"}, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        motel = self.get_object()
        motel.is_active = False
        motel.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ImageViewSet(viewsets.ViewSet, DestroySoftAPIView):
    serializer_class = ImageSerializer
    queryset = MotelImage.objects.filter(is_active=True).all()
    permission_classes = [perms.HasMotelOwnerAuthenticated]


class PriceViewSet(viewsets.ViewSet, DestroySoftAPIView, UpdatePartialAPIView):
    serializer_class = PriceSerializer
    queryset = Price.objects.filter(is_active=True).all()
    permission_classes = [perms.HasMotelOwnerAuthenticated]
