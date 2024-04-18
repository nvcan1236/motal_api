from rest_framework.serializers import ModelSerializer, SerializerMethodField
from motel.models import User, Follow, Motel, MotelImage, Price
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
        fields = ['id', 'username', 'avatar', 'first_name', 'last_name', 'user_role']


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
                                               'follower_count', 'following_count', 'password']
        extra_kwargs = {
            'password':
                {'write_only': True},
            'is_active':
                {'write_only': True}
        }


class MotelSerializer(ModelSerializer):
    class Meta:
        model = Motel
        fields = ['id', 'description', 'price', 'max_people', 'ward', 'district', 'city', 'other_address', 'area',
                  'owner']
        extra_kwargs = {
            'owner':
                {'read_only': True},
        }


class ImageSerializer(MotelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['url'] = instance.url.url
        return rep

    class Meta:
        model = MotelImage
        fields = ['id', 'url']


class PriceSerializer(MotelSerializer):
    class Meta:
        model = Price
        fields = ['id', 'label', 'value', 'period', 'motel']


class DetailMotelSerializer(MotelSerializer):
    motel_images = ImageSerializer(many=True, read_only=True)
    prices = PriceSerializer(many=True, read_only=True)

    def create(self, validated_data):
        data = validated_data.copy()
        motel = Motel(**data)
        motel.owner = self.context['request'].user
        motel.save()
        return motel

    class Meta:
        model = MotelSerializer.Meta.model
        fields = MotelSerializer.Meta.fields + ['lat', 'lon', 'motel_images', 'prices']
        extra_kwargs = MotelSerializer.Meta.extra_kwargs
