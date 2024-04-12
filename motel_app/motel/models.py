from django.db import models
from django.contrib.auth.models import AbstractUser
from enumchoicefield import EnumChoiceField
from enum import Enum


class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True)
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
    avatar = models.FileField(upload_to='motel/static/images/upload')
    user_role = EnumChoiceField(UserRole, default=UserRole.TENANT)
    phone = models.CharField(max_length=10)
    gender = EnumChoiceField(Gender, default=Gender.MALE)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', through='Follow')
    reservations = models.ManyToManyField('Motel', through='Reservation')


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_user')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_following')


class Motel(BaseModel):
    description = models.CharField(max_length=255)
    price = models.FloatField()
    max_people = models.IntegerField()
    xaphuong = models.CharField(max_length=255)
    quanhuyen = models.CharField(max_length=255)
    tinhtp = models.CharField(max_length=255)
    diachikhac = models.CharField(max_length=255)
    dientich = models.FloatField()
    lon = models.CharField(max_length=100)
    lat = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name='motels', on_delete=models.CASCADE)


class Utility(BaseModel):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    motel = models.ForeignKey(Motel, related_name='utilities', on_delete=models.CASCADE)


class Price(BaseModel):
    label = models.CharField(max_length=100)
    value = models.FloatField()
    motel = models.ForeignKey(Motel, related_name='prices', on_delete=models.CASCADE)


class Image(BaseModel):
    source = models.CharField(max_length=255)

    class Meta:
        abstract = True


class MotelImage(Image):
    motel = models.ForeignKey(Motel, related_name='motelimages', on_delete=models.CASCADE)


class Reservation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    motel = models.ForeignKey(Motel, on_delete=models.CASCADE)
