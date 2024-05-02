from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from motel.views import UpdatePartialAPIView, DestroySoftAPIView
from post.models import PostForRent, PostForLease, Post, Comment, Like
from post.serializers import PostForLeaseSerializer, PostForRentSerializer, PostSerializer, CommentSerializer, \
    BaseCommentSerializer, ReadPostForLeaseSerializer, ReadPostForRentSerializer
from motel import perms


class BasePostViewSet(viewsets.ViewSet, generics.ListCreateAPIView, UpdatePartialAPIView):
    # pass
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PostForLeaseViewSet(BasePostViewSet):
    serializer_class = PostForLeaseSerializer
    queryset = PostForLease.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ["get", "list"]:
            return ReadPostForLeaseSerializer

        return PostForLeaseSerializer

    def get_permissions(self):
        if self.action in ['partial_update']:
            return [perms.IsPostOwner()]
        elif self.action in ['create']:
            return [perms.IsOwner()]
        return [permissions.AllowAny()]


class PostForRentViewSet(BasePostViewSet):
    serializer_class = PostForRentSerializer
    queryset = PostForRent.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ["get", "list"]:
            return ReadPostForRentSerializer

        return PostForRentSerializer

    def get_permissions(self):
        if self.action in ['partial_update']:
            return [perms.IsPostOwner()]
        elif self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CommonPostViewSet(viewsets.ViewSet, DestroySoftAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['comment', 'like', ]:
            if self.request.method.__eq__("POST"):
                return [permissions.IsAuthenticated()]
            return [permissions.AllowAny()]
        elif self.action in ['destroy']:
            return [perms.OwnerAuthenticated()]
        else:
            return [permissions.AllowAny()]

    @action(methods=['get', 'post'], url_path="comments", detail=True)
    def comment(self, request, pk):
        if request.method.__eq__("GET"):
            comments = Comment.objects.filter(post=self.get_object(), is_active=True, reply_for=None)
            return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)
        elif request.method.__eq__("POST"):
            data = request.data.copy()
            data['post'] = self.get_object().id
            data['user'] = self.request.user.id

            serializer = BaseCommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        like, created = Like.objects.get_or_create(user=request.user, post=self.get_object())

        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            like.is_active = not like.is_active
            like.save()
            return Response(status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, DestroySoftAPIView, UpdatePartialAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.filter(is_active=True).all()
    permission_classes = [perms.OwnerAuthenticated]
