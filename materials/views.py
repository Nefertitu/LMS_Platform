from typing import Any, Sequence, Union

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from pyexpat.errors import messages
from rest_framework import filters, generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission, OperandHolder, SingleOperandHolder
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from materials.models import Course, Lesson, Payments, Subscription
from materials.paginators import MaterialsPaginator
from materials.serializers import CourseSerializer, LessonDetailSerializer, LessonSerializer, PaymentsSerializer, \
    SubscriptionSerializer
from users.permissions import IsModer, IsOwnerOnly


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPaginator

    PermissionClass = Union[
        type[BasePermission],
        OperandHolder,
        SingleOperandHolder
    ]

    def get_queryset(self) -> QuerySet[Course]:
        """Фильтрует курсы в зависимости от прав пользователя"""
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name="moders").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self) -> Sequence[Any]:
        """
        Управление разрешениями в зависимости от прав^
        модераторы (IsModer) могут только просматривать и редактировать
        любые курсы
        """

        if self.action == "create":
            self.permission_classes = [~IsModer, IsAuthenticated]
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = [IsModer | IsOwnerOnly]
        elif self.action == "destroy":
            self.permission_classes = [IsOwnerOnly]
        return super().get_permissions()

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        """Создает новый объект (Course) и автоматически назначает владельца (текущего пользователя)"""
        serializer.save(owner=self.request.user)


class LessonCreateAPIView(generics.CreateAPIView):
    """Представление для создания уроков"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = (~IsModer, IsAuthenticated)

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        """Создает новый объект (Lesson) и автоматически назначает владельца (текущего пользователя)"""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """Представление для списка уроков"""

    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwnerOnly,
    )
    pagination_class = MaterialsPaginator

    def get_queryset(self) -> QuerySet[Lesson]:
        """Фильтрует уроки в зависимости от прав пользователя"""
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name="moders").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Представление для получения конкретного урока"""

    serializer_class = LessonDetailSerializer
    queryset = Lesson.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwnerOnly,
    )


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Представление для обновления урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwnerOnly,
    )


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Представление для удаления урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwnerOnly | ~IsModer,
    )


class PaymentsViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с платежами"""

    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOnly)
    pagination_class = MaterialsPaginator

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


class SubscriptionAPIView(generics.CreateAPIView):
    """Представления для управления подписками пользователя на курсы"""

    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """POST-метод для обработки запроса на активацию/деактивацию подписки"""

        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = self.request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        subs_item, created = Subscription.objects.get_or_create(user=user, course=course, defaults={"is_active": True})

        if not created:
            subs_item.is_active = not subs_item.is_active
            subs_item.save()
            message = "Подписка удалена" if not subs_item.is_active else "Подписка добавлена"

        else:
            subs_item.save()
            message = "Подписка добавлена"

        response_serializer = self.get_serializer(subs_item)

        return Response({
            **response_serializer.data,
            "message": message,
        },
            status=status.HTTP_200_OK,
        )

class SubscriptionCoursesAPIView(generics.ListAPIView):
        """Представление для получения списка активных подписок пользователя"""

        serializer_class = SubscriptionSerializer
        queryset = Subscription.objects.all()
        permission_classes = [IsAuthenticated, IsOwnerOnly]
        pagination_class = MaterialsPaginator

        def get_queryset(self) -> QuerySet[Subscription]:
            """Фильтрует курсы в зависимости от прав пользователя"""
            user = self.request.user

            if not user.is_authenticated:
                return Subscription.objects.none()

            return Subscription.objects.filter(user=user, is_active=True).select_related("course")

