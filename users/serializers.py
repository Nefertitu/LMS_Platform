from rest_framework import serializers

from materials.models import Payments
from materials.serializers import PaymentsSerializer
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Пользователь"""

    payments = serializers.SerializerMethodField()

    def get_payments(self, obj: User) -> dict:
        """Возвращает список платежей пользователей"""
        payments = Payments.objects.filter(user=obj).select_related("course", "lesson")
        return PaymentsSerializer(payments, many=True).data

    class Meta:
        model = User
        fields = (
            "id",
            "password",
            "email",
            "phone",
            "city",
            "avatar",
            "payments",
        )
        # extra_kwargs = {"password": {"write_only": True}}


class PublicUserSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = User
        fields = (
            "email",
            "city",
            "avatar",
        )

