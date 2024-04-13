from rest_framework.serializers import ModelSerializer, SerializerMethodField
from motel.models import User, Follow
from cloudinary.models import CloudinaryResource


class HaveImageSerializer(ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url
        return rep


class UserSerializer(ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url
        return rep

    class Meta:
        model = User
        fields = ['username', 'avatar', 'first_name', 'last_name', 'user_role', 'password']


class DetailUserSerializer(UserSerializer):
    follower_count = SerializerMethodField()
    following_count = SerializerMethodField()

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()
        return user

    def get_follower_count(self, obj):
        return Follow.objects.filter(following=obj, is_active=True).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj, is_active=True).count()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ['gender', 'date_joined', 'last_login', 'email', 'phone',
                                               'follower_count', 'following_count']
