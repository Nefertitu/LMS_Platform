from decimal import Decimal
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_serializer_method
from pydantic import ValidationError
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from users.models import Payment, User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Пользователь"""

    payments = serializers.SerializerMethodField()

    def get_payments(self, obj: User) -> dict:
        """Возвращает список платежей пользователей"""
        payments = Payment.objects.filter(user=obj).select_related("course", "lesson")
        return PaymentSerializer(payments, many=True).data

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


class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'PublicUserSerializer'"""

    class Meta:
        model = User
        fields = (
            "email",
            "city",
            "avatar",
        )


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Payment'"""

    price = SerializerMethodField()
    title = SerializerMethodField()

    def get_price(self, obj: Payment) -> Optional[str]:
        """Возвращает стоимость урока или курса"""
        if obj.lesson and hasattr(obj.lesson, "price"):
            return f"{obj.lesson.price} руб."
        elif obj.course and hasattr(obj.course, "price"):
            return f"{obj.course.price} руб."
        else:
            raise ValidationError("У продукта не указана цена")

    def get_title(self, obj: Payment) -> Optional[str]:
        """Возвращает название урока или курса"""
        if obj.lesson and hasattr(obj.lesson, "title"):
            return obj.lesson.title
        elif obj.course and hasattr(obj.course, "course_title"):
            return obj.course.course_title
        else:
            raise ValidationError("У продукта нет названия")

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Сериализатор детального отображения итогов платежа для модели 'Payment'"""

    title = SerializerMethodField()
    payment_status = SerializerMethodField()
    payment_amount = SerializerMethodField()
    payment_currency = SerializerMethodField()
    customer_email = SerializerMethodField()
    payment_method = SerializerMethodField()

    def get_title(self, obj: Payment) -> Optional[str]:
        """Возвращает название урока или курса"""
        if obj.lesson and hasattr(obj.lesson, "title"):
            return obj.lesson.title
        elif obj.course and hasattr(obj.course, "course_title"):
            return obj.course.course_title
        else:
            raise ValidationError("У продукта нет названия")

    def get_payment_status(self, obj: Payment) -> Optional[str]:
        """Возвращает статус платежа"""
        return (
            getattr(obj, "stripe_status", None) if obj.payment_method == "transfer" else getattr(obj, "status", None)
        )

    def get_payment_amount(self, obj: Payment) -> Optional[Decimal]:
        """Возвращает сумму платежа в рублях с преобразованием из копеек"""

        if obj.lesson:
            price = obj.lesson.price
        elif obj.course:
            price = obj.course.price
        else:
            raise ValidationError("У продукта не установлена цена")

        amount = getattr(obj, "stripe_amount", None) if obj.payment_method == "transfer" else price * 100
        return Decimal(amount) / 100 if amount is not None else None

    def get_payment_currency(self, obj: Payment) -> Optional[str]:
        """Возвращает валюту платежа"""
        return getattr(obj, "stripe_currency", None) if obj.payment_method == "transfer" else "rub"

    def get_customer_email(self, obj: Payment) -> Optional[str]:
        """Возвращает 'email' покупателя"""

        if obj is None:
            return None

        if obj.payment_method == Payment.CASH:
            return obj.user.email if obj.user else None
        return obj.customer_email

    def get_payment_method(self, obj: Payment) -> Optional[str]:
        """Возвращает способ оплаты"""

        if obj is None:
            return None

        payment_method = getattr(obj, "payment_method", None)

        if payment_method == Payment.CASH:
            return None
        elif payment_method == Payment.TRANSFER:
            return "Банковский перевод через Stripe"

        return None

    class Meta:
        model = Payment
        fields = (
            "id",
            "title",
            "payment_status",
            "payment_amount",
            "payment_currency",
            "customer_email",
            "payment_method",
        )
