from time import strptime
from typing import Optional

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson, Payments


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Course'"""

    lessons = SerializerMethodField()

    def get_lessons(self, course: Course) -> list:
        """"""
        return [lesson.title for lesson in Lesson.objects.filter(course=course)]

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Lesson'"""

    course = CourseSerializer()

    class Meta:
        model = Lesson
        fields = "__all__"


class LessonDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Урок с дополнительной информацией о количестве уроков
    того же курса"""

    count_lessons_one_course = SerializerMethodField()
    course_title = serializers.CharField(source="course.course_title", allow_null=True)

    def get_count_lessons_one_course(self, lesson: Lesson) -> int:
        """Подсчитывает количество уроков курса"""
        return Lesson.objects.filter(course=lesson.course).count()

    class Meta:
        model = Lesson
        fields = ("id", "title", "course_title", "description", "link", "count_lessons_one_course")


class PaymentsSerializer(ModelSerializer):
    """Сериализатор для модели 'Payments'.
    Преобразует данные о платежах в формат API"""

    amount = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    def get_amount(self, instance: Payments) -> Optional[str]:
        """Возвращает сумму платежа с указанием валюты"""
        return f"{instance.amount} руб." if instance.amount else None

    def get_payment_date(self, instance: Payments) -> Optional[str]:
        """Форматирует дату платежа в строку"""
        return instance.payment_date.strftime("%d.%m.%Y %H:%m") if instance.payment_date else None

    def get_lesson(self, instance: Payments) -> Optional[str]:
        """Возвращает название урока"""
        return instance.lesson.title if instance.lesson else None

    def get_course(self, instance: Payments) -> Optional[str]:
        """Возвращает название курса"""
        return instance.course.course_title if instance.course else None

    def get_user_email(self, instance: Payments) -> Optional[str]:
        """Возвращает email пользователя"""
        return instance.user.email if instance.user else None

    class Meta:
        model = Payments
        fields = (
            "id",
            "amount",
            "payment_date",
            "payment_method",
            "course",
            "lesson",
            "user_email",
        )
