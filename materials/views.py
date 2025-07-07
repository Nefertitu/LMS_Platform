from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets

from materials.models import Course, Lesson, Payments
from materials.serializers import CourseSerializer, LessonDetailSerializer, LessonSerializer, PaymentsSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами"""

    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class LessonCreateAPIView(generics.CreateAPIView):
    """Представление для создания уроков"""

    serializer_class = LessonSerializer


class LessonListAPIView(generics.ListAPIView):
    """Представление для списка уроков"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Представление для получения конкретного урока"""

    serializer_class = LessonDetailSerializer
    queryset = Lesson.objects.all()


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Представление для обновления урока"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Представление для удаления урока"""

    queryset = Lesson.objects.all()


class PaymentsViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с платежами"""

    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
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
    search_fields = (
        "course__course_title",
        "lesson__title",
        "user__email")
