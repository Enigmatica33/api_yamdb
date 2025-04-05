from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrReadOnlyCustom(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            # Исключение 401 для неавторизованных POST/DELETE
            raise AuthenticationFailed(
                detail='Прав не достаточно.',
                code='not_authenticated'
            )
        return request.user.is_admin


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
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
        )
