from typing import Any

from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request


class IsOwnerOnly(permissions.BasePermission):
    """Разрешение только для владельца объекта"""

    def has_object_permission(self, request: Request, view: Any, obj: Model) -> bool:
        """Проверяет, является ли пользователь владельцем объекта"""
        return obj == request.user


class IsModer(permissions.BasePermission):
    """Разрешение только для владельца объекта"""

    def has_permission(self, request: Request, view: Any) -> bool:
        """Проверяет, является ли пользователь владельцем объекта"""
        return request.user.proups.filter(name="moders").exists()