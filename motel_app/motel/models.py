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
    avatar = models.CharField()
    user_role = EnumChoiceField(UserRole, default=UserRole.TENANT)
    phone = models.CharField(max_length=10, blank=False)
    gender = EnumChoiceField(Gender, default=Gender.MALE)


# Tro: id, giathue, soluongnguoi, kichthuoc, xaphuong, quanhuyen, tinhtp, diachikhac, mota
class Motel(models.Model):
    description = models.CharField(max_length=255)
    price = models.FloatField(blank=False)
    max_people = models.IntegerField()


