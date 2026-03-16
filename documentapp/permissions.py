from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Allow only authenticated users with is_staff=True (admin/staff access)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsAdminUser(BasePermission):
    """Allow only authenticated users with role ADMIN."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMIN"
        )


