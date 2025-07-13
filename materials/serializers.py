from typing import Optional

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson, Payments, Subscription
from materials.validators import LinkValidator
from users.models import User


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Course'"""

    lessons = SerializerMethodField()
    lessons_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    def get_lessons(self, course: Course) -> list:
        """Возвращает список названий уроков для данного курса"""
        return [lesson.title for lesson in Lesson.objects.filter(course=course)]

    def get_lessons_count(self, course: Course) -> int:
        """Возвращает количество уроков, связанных с данным курсом"""

        return course.lessons.count()

    def get_is_subscribed(self, user: User) -> list:
        """Возвращает список email-адресов подписчиков для данного курса"""
        return [user.user.email for user in Subscription.objects.filter(is_active=True)]

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Lesson'"""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [LinkValidator(field="link")]


class LessonDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Lesson' с дополнительной информацией о количестве уроков
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

class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Subscription'"""

    course_title = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_course_title(self, instance: Subscription) -> Optional[str]:
        """Возвращает название курса данной подписки"""
        return str(instance.course.course_title) if instance.course else None

    def get_user_email(self, instance: Subscription) -> Optional[str]:
        """Возвращает email пользователя-подписчика"""
        return str(instance.user.email) if instance.user else None

    def get_created_at(self, instance: Subscription) -> Optional[str]:
        """Форматирует дату создания подписки в строку"""
        return instance.created_at.strftime("%d.%m.%Y %H:%m") if instance.created_at else None

    class Meta:
        model = Subscription
        fields = (
            "id",
            "user_email",
            "course_title",
            "is_active",
            "created_at",
        )
