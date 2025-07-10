from typing import List

from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.models import User
from users.permissions import IsOwnerOnly
from users.serializers import UserProfileSerializer

class UserCreateApiView(CreateAPIView):
    """Класс для создания профиля пользователя"""

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Метод для создания профиля пользователя (POST /register/)"""

        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

class UserProfileViewSet(viewsets.ModelViewSet):
    """Управление пользователями (требуется аутентификация)"""

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Управление разрешениями:
        (GET /users/        # Список (для админов)
        GET /users/{id}/    # Просмотр
        PUT /users/{id}/    # Полное обновление
        PATCH /users/{id}/  # Частичное обновление
        DELETE /users/{id}/ # Удаление (только админы)
        )
        """

        if self.action in ["list", "destroy"]:
            return [permissions.IsAdminUser()]
        elif self.action in ["update", "partial_update"]:
            return [IsOwnerOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self) -> QuerySet:
        """Фильтрация данных - обычные пользователи видят только свой профиль,
        админы - все"""

        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(pk=self.request.user.pk)

    def perform_update(self, serializer) -> None:
        """Метод для выполнения дополнительной обработки при обновлении"""

        if "password" in serializer.validated_data:
            serializer.instance.set_password(serializer.validated_data["password"])
        serializer.save()


