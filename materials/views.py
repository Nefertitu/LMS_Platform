from typing import Any, Sequence, Union, List

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, serializers, viewsets
from rest_framework.permissions import OR, IsAuthenticated, BasePermission, OperandHolder, SingleOperandHolder
from rest_framework.serializers import BaseSerializer

from materials.models import Course, Lesson, Payments
from materials.serializers import CourseSerializer, LessonDetailSerializer, LessonSerializer, PaymentsSerializer
from users.permissions import IsModer, IsOwnerOnly


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

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
