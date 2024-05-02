from rest_framework.serializers import ModelSerializer, SerializerMethodField

from motel.serializers import MotelSerializer, UserSerializer, HaveImageSerializer
from post.models import Post, PostForLease, PostForRent, Like, Comment, User


class PostSerializer(ModelSerializer):
    like_count = SerializerMethodField()
    comment_count = SerializerMethodField()

    def get_like_count(self, obj):
        return Like.objects.filter(is_active=True, post=obj).count()

    def get_comment_count(self, obj):
        return Comment.objects.filter(is_active=True, post=obj).count()

    class Meta:
        model = Post
        fields = ['id', 'content', 'user', 'created_date',
                  'like_count', 'comment_count']


class PostForLeaseSerializer(PostSerializer):
    class Meta:
        model = PostForLease
        fields = PostSerializer.Meta.fields + ['motel']


class ReadPostForLeaseSerializer(PostForLeaseSerializer):
    motel = MotelSerializer(read_only=True)
    user = UserSerializer(read_only=True)


class PostForRentSerializer(PostSerializer, HaveImageSerializer):
    class Meta:
        model = PostForRent
        fields = PostSerializer.Meta.fields + ['ward', 'district', 'city', 'other_address', 'image']


class ReadPostForRentSerializer(PostForRentSerializer):
    user = UserSerializer(read_only=True)


class BaseCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created_date', 'post']


class CommentSerializer(BaseCommentSerializer):
    replies = BaseCommentSerializer(many=True, read_only=True)
    user = UserSerializer()

    class Meta:
        model = BaseCommentSerializer.Meta.model
        fields = BaseCommentSerializer.Meta.fields + ['replies']
