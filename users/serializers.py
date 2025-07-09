from rest_framework import serializers
from rest_framework.authtoken.models import Token

from materials.models import Payments
from materials.serializers import PaymentsSerializer
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Пользователь"""

    # token = serializers.SerializerMethodField(read_only=True)
    payments = serializers.SerializerMethodField()

    # def get_token(self, obj: User) -> Any:
    #     """Получает или создает токен аутентификации для пользователя"""
    #
    #     token, _ = Token.objects.get_or_create(user=obj)
    #     return token.key

    def get_payments(self, obj: User) -> dict:
        """Возвращает список платежей пользователей"""
        payments = Payments.objects.filter(user=obj).select_related("course", "lesson")
        return PaymentsSerializer(payments, many=True).data

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            # "token",
            "payments",
        )
        extra_kwargs = {"password": {"write_only": True}}
