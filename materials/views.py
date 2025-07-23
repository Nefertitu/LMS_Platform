from datetime import timedelta
from typing import Any, Sequence, Union

from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated, OperandHolder, SingleOperandHolder
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialsPaginator
from materials.serializers import (
    CourseSerializer,
    LessonDetailSerializer,
    LessonSerializer,
    SubscriptionSerializer,
)
from users.permissions import IsModer, IsOwnerOnly
from .tasks import notify_subscriber


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPaginator

    PermissionClass = Union[type[BasePermission], OperandHolder, SingleOperandHolder]

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

    def update(self, request, *args, **kwargs):
        """Обновление курса"""

        instance = self.get_object()
        previous_update_time = instance.updated_at

        # subscription = Subscription.objects.filter(course=instance, is_active=True)
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        now = timezone.now()
        four_hours_ago = now - timedelta(seconds=60)  # 14400 сек. = 4 часа

        if previous_update_time < four_hours_ago:
            subscription = Subscription.objects.filter(course=instance, is_active=True)

            for subs in subscription:
                notify_subscriber.delay(subs.pk)
                print(f"Задача отправки уведомления для подписки {subs.pk} запущена")

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


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

        return Response(
            {
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
