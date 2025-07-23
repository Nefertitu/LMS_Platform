import os
from decimal import Decimal, InvalidOperation
from typing import Any, List, cast

from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from users.models import Payment, User
from users.paginators import UsersPaginator
from users.permissions import IsModer, IsOwnerOnly
from users.serializers import PaymentDetailSerializer, PaymentSerializer, PublicUserSerializer, UserProfileSerializer
from users.services import (
    create_retrieves_a_checkout_session,
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
)


class UserCreateApiView(CreateAPIView):
    """Класс для создания профиля пользователя"""

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        """Метод для создания профиля пользователя (POST /register/)"""

        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserProfileViewSet(viewsets.ModelViewSet):
    """Управление пользователями (требуется аутентификация)"""

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get_serializer_class(self) -> type[serializers.BaseSerializer]:
        """Динамический выбор сериализатора"""

        if self.action == "list":
            if not (self.request.user.is_staff):
                return PublicUserSerializer

        elif self.action == "retrieve":
            object = self.get_object()
            if not (self.request.user.is_staff or self.request.user == object.email):
                return PublicUserSerializer

        return UserProfileSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Управление разрешениями:
        (GET /users/        # Список
        GET /users/{id}/    # Просмотр
        PUT /users/{id}/    # Полное обновление (только владелец)
        PATCH /users/{id}/  # Частичное обновление (только владелец)
        DELETE /users/{id}/ # Удаление (только админы)
        )
        """

        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "destroy":
            return [permissions.IsAdminUser()]
        elif self.action in ["update", "partial_update"]:
            return [IsOwnerOnly()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer: BaseSerializer[Any]) -> None:
        """Метод для выполнения дополнительной обработки при обновлении"""

        if "password" in serializer.validated_data:
            user = cast(User, serializer.instance)
            user.set_password(serializer.validated_data["password"])
        serializer.save()


class PaymentCreateAPIView(CreateAPIView):
    """API эндпоинт для создания платежа в системе Stripe"""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = (IsAuthenticated,)

    pagination_class = UsersPaginator

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = (
        "course",
        "lesson",
        "payment_method",
    )
    ordering_fields = (
        "payment_date",
        "amount",
    )
    search_fields = ("course__course_title", "lesson__title", "user__email")

    def perform_create(self, serializer: BaseSerializer[Payment]) -> None:
        """Создает платеж и связанные сущности в Stripe."""

        payment = serializer.save(user=self.request.user)
        # payment = cast(Payment, serializer.instance)

        product_name = payment.course or payment.lesson
        if not product_name:
            raise ValidationError("Платеж должен быть привязан к курсу или уроку")

        if payment.course and hasattr(payment.course, "price"):
            product_price = payment.course.price
        elif payment.lesson and hasattr(payment.lesson, "price"):
            product_price = payment.lesson.price
        else:
            raise ValidationError("У продукта отсутствует цена")

        if payment.payment_method == Payment.CASH:
            payment.status = Payment.STATUS_PENDING
            payment.save()

        try:
            stripe_product = create_stripe_product(product_name)
            stripe_price = create_stripe_price(stripe_product, product_price)

            session_id, payment_link = create_stripe_session(stripe_price)

            stripe_data = create_retrieves_a_checkout_session(session_id)

            payment.session_id = session_id
            payment.link = payment_link
            # payment.status = Payment.STATUS_PENDING
            payment.stripe_status = stripe_data["status"]
            payment.status = stripe_data["status"]
            payment.stripe_amount = stripe_data.get("amount")
            payment.stripe_currency = stripe_data.get("currency", "rub")
            payment.customer_email = stripe_data.get("email")
            payment.stripe_payment_intent_id = stripe_data.get("payment_intent_id")

            payment.save()

        except Exception as e:
            print(f"Payment creation error: {e}")
            raise ValidationError("Ошибка при создании платежа в Stripe")


class ConfirmCashPaymentAPIView(UpdateAPIView):
    """API эндпоинт для подтверждения платежа наличными"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminUser | IsOwnerOnly,
        ~IsModer,
    )
    lookup_field = "pk"

    def perform_update(self, serializer: BaseSerializer[Any]) -> None:
        """Подтверждает платеж наличными и отправляет уведомление пользователю по email"""

        payment = cast(Payment, serializer.instance)

        if not payment or not isinstance(payment, Payment):
            raise ValidationError({"detail": "Неверный объект платежа"})

        if payment.payment_method != Payment.CASH:
            raise ValidationError({"detail": "Можно подтверждать только наличные платежи"})

        if payment.status != Payment.STATUS_PENDING:
            raise ValidationError({"detail": "Платеж уже был обработан"})

        if payment.lesson:
            product_name = payment.lesson.title
            product_amount = payment.lesson.price
        elif payment.course:
            product_name = payment.course.course_title
            product_amount = payment.course.price
        else:
            raise ValidationError({"detail": "Платеж должен быть связан с курсом или уроком"})
        # link = [payment.lesson.link if payment.lesson else payment.course.link]
        payment.status = Payment.STATUS_PAID
        serializer.save(status=Payment.STATUS_PAID)

        if not payment.user or not payment.user.email:
            raise ValidationError({"detail": "Не указан email пользователя"})

        send_mail(
            f"Подтвержден платеж на доступ к {product_name}",
            f"Платеж #{payment.pk} на сумму {product_amount} подтвержден.",
            # f'Ссылка на урок: {link}',
            os.getenv("EMAIL_HOST_USER"),
            [payment.user.email],
            fail_silently=False,
        )


class PaymentRetrieveAPIView(RetrieveAPIView):
    """API эндпоинт для получения детальной информации о платеже"""

    serializer_class = PaymentDetailSerializer
    queryset = Payment.objects.all()

    def retrieve(self, *args: Any, **kwargs: Any) -> Response:
        """Возвращает детальную информацию о платеже со статусом из Stripe"""
        payment = self.get_object()
        response_data = {}

        if payment.session_id and payment.payment_method == Payment.TRANSFER:
            stripe_data = create_retrieves_a_checkout_session(payment.session_id)
            payment.stripe_status = stripe_data.get("status")
            payment.stripe_amount = stripe_data.get("amount")
            payment.stripe_currency = stripe_data.get("currency")
            payment.customer_email = stripe_data.get("email")
            payment.stripe_payment_intent_id = stripe_data.get("payment_intent_id")

            payment.save()

        elif payment.payment_method == Payment.CASH:
            response_data.update(
                {
                    "payment_method": "cash",
                    "payment_status": payment.status,
                }
            )

        serializer = self.get_serializer(payment)
        return Response(serializer.data)
