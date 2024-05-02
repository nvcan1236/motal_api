from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from enumchoicefield import EnumChoiceField
from enum import Enum
from cloudinary.models import CloudinaryField

EXPIRATION_RESERVATION = 3


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class UserRole(Enum):
    MOTEL_OWNER = 'Chu tro',
    TENANT = 'Nguoi thue tro'


class Gender(Enum):
    MALE = 'Nam'
    FEMALE = 'Nu'
    OTHER = 'Khac'


class User(AbstractUser):
    avatar = CloudinaryField()
    user_role = EnumChoiceField(UserRole, default=UserRole.TENANT)
    phone = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    gender = EnumChoiceField(Gender, default=Gender.MALE)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', through='Follow')
    reservations = models.ManyToManyField('Motel', through='Reservation')


class Follow(BaseModel):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_user')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_following')

    class Meta:
        unique_together = ('follower', 'following')


class Motel(BaseModel):
    description = models.CharField(max_length=500)
    price = models.FloatField()
    furniture = models.CharField(max_length=255)
    max_people = models.IntegerField()
    ward = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    other_address = models.CharField(max_length=255)
    area = models.FloatField()
    lon = models.CharField(max_length=100)
    lat = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name='motels', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)


class PriceEnum(Enum):
    WATER = 'Nuoc'
    ELECTRICITY = 'Dien'
    INTERNET = 'Internet'
    OTHER = 'Khac'


class Price(BaseModel):
    label = EnumChoiceField(PriceEnum)
    name = models.CharField(max_length=100)
    value = models.FloatField()
    period = models.CharField(max_length=255)
    motel = models.ForeignKey(Motel, related_name='prices', on_delete=models.CASCADE)


class MotelImage(BaseModel):
    url = CloudinaryField()
    motel = models.ForeignKey(Motel, related_name='images', on_delete=models.CASCADE)


class Reservation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    motel = models.ForeignKey(Motel, on_delete=models.CASCADE)
    expiration = models.DateTimeField(null=False,
                                      default=(datetime.now() + timedelta(days=EXPIRATION_RESERVATION)).strftime(
                                          "%Y-%m-%d %H:%M:%S"))
