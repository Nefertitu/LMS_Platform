from typing import List, Optional

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import User
from users.serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ViewSet):
    """ViewSet для редактирования профиля пользователя"""

    def get_permissions(self) -> List[permissions.BasePermission]:
        """Разрешение создания пользователя без аутентификации"""

        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action == "list":
            return [permissions.IsAdminUser()]
        elif self.action == "destroy":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def list(self, request: Request) -> Response:
        """Метод для вывода списка пользователей"""

        queryset = User.objects.all()
        serializer = UserProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, pk: int) -> Response:
        """Получить пользователя по ID (GET /users/<pk>/)"""

        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def create(self, request: Request) -> Response:
        """Метод для создания профиля пользователя (POST /users/)"""

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, pk: int) -> Response:
        """Метод для редактирования профиля пользователя (PUT /users/<pk>/)"""

        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request: Request, pk: int) -> Response:
        """Частично обновить пользователя (PATCH /users/<pk>/)"""

        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, pk: Optional[int]) -> Response:
        """Метод для удаления профиля пользователя (PUT /users/<pk>/)"""

        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
