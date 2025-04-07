from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение: только для админов (включая staff/superuser)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or request.user.is_staff
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение: только для админов на запись, остальным — только чтение."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or request.user.is_staff
        )


class IsAuthorOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """Разрешение: автор, модератор, админ — ред., др — только чтение."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
            or request.user.is_superuser
            or request.user.is_staff
        )
