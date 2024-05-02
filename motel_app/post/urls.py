from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from post.views import PostForLeaseViewSet, PostForRentViewSet, CommonPostViewSet, CommentViewSet

router = routers.DefaultRouter()

router.register('for_lease', PostForLeaseViewSet, 'postforlease')
router.register('for_rent', PostForRentViewSet, 'postforrent')
router.register('', CommonPostViewSet, 'post')
router.register('comments', CommentViewSet, 'comment')

urlpatterns = [
    path('', include(router.urls))
]
