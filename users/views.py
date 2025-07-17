from typing import Any, List, cast

from rest_framework import permissions, serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from stripe.forwarding import Request

from users.models import Payment, User
from users.permissions import IsOwnerOnly
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
        stripe_product = create_stripe_product(product_name)
        stripe_price = create_stripe_price(stripe_product, product_price)
        session_id, link = create_stripe_session(stripe_price)
        payment.session_id = session_id
        payment.link = link
        payment.save()


class PaymentRetrieveAPIView(RetrieveAPIView):
    """API эндпоинт для получения детальной информации о платеже"""

    serializer_class = PaymentDetailSerializer
    queryset = Payment.objects.all()

    def retrieve(self, *args: Any, **kwargs: Any) -> Response:
        """Возвращает детальную информацию о платеже со статусом из Stripe"""

        obj = self.get_object()
        if obj.session_id:
            session_status = create_retrieves_a_checkout_session(obj.session_id)
            obj.stripe_status = session_status.get("status")
            obj.stripe_amount = session_status.get("amount")
            obj.stripe_currency = session_status.get("currency")
            obj.stripe_email = session_status.get("email")

        serializer = self.get_serializer(obj)
        return Response(serializer.data)
