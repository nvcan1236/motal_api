from rest_framework import permissions
from motel.models import UserRole


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj == request.user


class OwnerAuthenticated(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj.user == request.user


class IsMotelOwner(permissions.IsAuthenticated):
    # User đăng nhập với role chủ trọ
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.user_role == UserRole.MOTEL_OWNER


class MotelOwnerAuthenticated(IsMotelOwner):
    # Đối tượng user là chủ trọ của đối tượng motel
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and obj.owner == request.user
