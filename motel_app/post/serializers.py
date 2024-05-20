from rest_framework.serializers import ModelSerializer, SerializerMethodField

from motel.serializers import UserSerializer, HaveImageSerializer, DetailMotelSerializer
from post.models import Post, PostForLease, PostForRent, Like, Comment


class PostSerializer(ModelSerializer):
    like_count = SerializerMethodField()
    comment_count = SerializerMethodField()
    liked = SerializerMethodField()

    def get_like_count(self, obj):
        return Like.objects.filter(is_active=True, post=obj).count()

    def get_comment_count(self, obj):
        return Comment.objects.filter(is_active=True, post=obj).count()

    def get_liked(self, obj):
        if self.context['request'].user.id:
            return Like.objects.filter(user=self.context['request'].user, post=obj).first() is not None
        return False

    class Meta:
        model = Post
        fields = ['id', 'content', 'user', 'created_date',
                  'like_count', 'comment_count', 'liked']


class PostForLeaseSerializer(PostSerializer):
    class Meta:
        model = PostForLease
        fields = PostSerializer.Meta.fields + ['motel']


class ReadPostForLeaseSerializer(PostForLeaseSerializer):
    motel = DetailMotelSerializer(read_only=True)
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
        fields = ['id', 'content', 'user', 'created_date', 'post', 'reply_for']


class CommentSerializer(BaseCommentSerializer):
    replies = BaseCommentSerializer(many=True, read_only=True)
    user = UserSerializer()

    class Meta:
        model = BaseCommentSerializer.Meta.model
        fields = BaseCommentSerializer.Meta.fields + ['replies']
