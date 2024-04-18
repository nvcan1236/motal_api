from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from motel.views import UserViewSet, MotelViewSet

router = routers.DefaultRouter()
router.register('user', UserViewSet, 'user')
router.register('motels', MotelViewSet, 'motel')


urlpatterns = [
    path('', include(router.urls))
]