import os
from typing import Any, List, cast

from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from stripe.forwarding import Request

from users.models import Payment, User
from users.paginators import UsersPaginator
from users.permissions import IsOwnerOnly, IsModer
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
        product_name = payment.course if payment.course else payment.lesson

        if product_name is None:
            raise ValidationError("Платеж должен быть связан с курсом или с уроком")
        if payment.course and hasattr(payment.course, "price"):
            product_price = payment.course.price
        elif payment.lesson and hasattr(payment.lesson, "price"):
            product_price = payment.lesson.price
        else:
            raise ValidationError("Продукт не имеет цены")

        if payment.payment_method == "cash":
            payment.status = "pending"
            payment.amount = product_price
            payment.save()

        else:
            stripe_product = create_stripe_product(product_name)
            stripe_price = create_stripe_price(stripe_product, product_price)
            session_id, link = create_stripe_session(stripe_price)
            payment.session_id = session_id
            payment.link = link
            payment.status = "pending"
            payment.save()


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

    def perform_update(self, serializer):
        payment = serializer.instance

        if payment.payment_method != "cash":
            raise ValidationError({"detail": "Можно подтверждать только наличные платежи"})

        if payment.status != "pending":
            raise ValidationError({"detail": "Платеж уже был обработан"})

        product_name = payment.lesson.title if payment.lesson else payment.course.course_title
        product_amount = payment.lesson.price if payment.lesson else payment.course.price
        # link = [payment.lesson.link if payment.lesson else payment.course.link]
        payment.status = "paid"
        serializer.save(status="paid")

        send_mail(
            f"Подтвержден платеж на доступ к {product_name}",
            f"Платеж #{payment.id} на сумму {product_amount} подтвержден.",
            # f'Ссылка на урок: {link}',
            os.getenv("EMAIL_HOST_USER"),
            [payment.user.email],
            fail_silently=False
            )


class PaymentRetrieveAPIView(RetrieveAPIView):
    """API эндпоинт для получения детальной информации о платеже"""

    serializer_class = PaymentDetailSerializer
    queryset = Payment.objects.all()

    def retrieve(self, *args: Any, **kwargs: Any) -> Response:
        """Возвращает детальную информацию о платеже со статусом из Stripe"""
        payment = self.get_object()
        response_data = {}

        if payment.session_id:
            session_status = create_retrieves_a_checkout_session(payment.session_id)
            payment.stripe_status = session_status.get("status")
            payment.stripe_amount = session_status.get("amount")
            payment.stripe_currency = session_status.get("currency")
            payment.stripe_email = session_status.get("email")
            response_data.update({
                "stripe_status": payment.stripe_status,
                "stripe_amount": payment.stripe_amount,
                "stripe_currency": payment.stripe_currency,
                "payment_method": payment.payment_method,
            })

        elif payment.payment_method == "cash":
            response_data.update({
                "payment_method": "cash",
                "payment_status": payment.status,
            })


        serializer = self.get_serializer(payment)
        return Response(serializer.data)
