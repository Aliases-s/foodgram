"""Права доступа API проекта."""

from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Изменять объект может только его автор."""

    def has_object_permission(self, request, view, obj):
        """Разрешает запись только автору объекта."""
        return request.method in SAFE_METHODS or obj.author == request.user
