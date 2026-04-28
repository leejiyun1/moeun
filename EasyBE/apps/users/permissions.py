from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow only authenticated users with the ADMIN role."""

    message = "관리자 권한이 필요합니다."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_admin", False))
