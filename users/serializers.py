from typing import Any

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Пользователь"""

    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "phone", "city", "avatar", "token"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_token(self, obj: User) -> Any:
        """Получает или создает токен аутентификации для пользователя"""

        token, _ = Token.objects.get_or_create(user=obj)
        return token.key
