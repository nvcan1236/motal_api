from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from motel.views import UserViewSet, MotelViewSet, ImageViewSet, PriceViewSet

router = routers.DefaultRouter()
router.register('user', UserViewSet, 'user')
router.register('motels', MotelViewSet, 'motel')
router.register('motels/images', ImageViewSet, 'motelimage')
router.register('motels/prices', PriceViewSet, 'price')

urlpatterns = [
    path('', include(router.urls))
]
