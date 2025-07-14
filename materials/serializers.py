from typing import Optional

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson, Payments, Subscription
from materials.validators import LinkValidator


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Course'"""

    lessons = SerializerMethodField()
    lessons_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()
    owner = SerializerMethodField()

    def get_lessons(self, course: Course) -> list:
        """Возвращает список названий уроков для данного курса"""
        return [lesson.title for lesson in Lesson.objects.filter(course=course)]

    def get_lessons_count(self, course: Course) -> int:
        """Возвращает количество уроков, связанных с данным курсом"""

        return course.lessons.count()

    def get_is_subscribed(self, course: Course) -> list[str]:
        """Возвращает список email-адресов подписчиков для данного курса"""
        return [
            subscription.user.email
            for subscription in Subscription.objects.filter(is_active=True, course=course)
            if subscription.user
        ]

    def get_owner(self, course: Course) -> list[str]:
        """Возвращает список email-адресов подписчиков для данного курса"""
        return [course.owner.email for course in Course.objects.filter(owner=course.owner) if course.owner]

    class Meta:
        model = Course
        fields = ("id", "course_title", "preview", "description", "owner", "is_subscribed", "lessons", "lessons_count")


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели 'Lesson'"""

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    course_title = SerializerMethodField()

    def get_course_title(self, instance: Lesson) -> Optional[str]:
        """Возвращает название курса"""
        return instance.course.course_title if instance.course else None

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

    amount_str = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    course_owner_email = serializers.SerializerMethodField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2, write_only=True, required=True)

    def get_amount_str(self, instance: Payments) -> Optional[str]:
        """Возвращает сумму платежа с указанием валюты"""
        return f"{instance.amount} руб." if instance.amount else None

    def get_payment_date(self, instance: Payments) -> Optional[str]:
        """Форматирует дату платежа в строку"""
        return instance.payment_date.strftime("%d.%M.%Y %H:%m") if instance.payment_date else None

    def get_lesson(self, instance: Payments) -> Optional[str]:
        """Возвращает название урока"""
        return instance.lesson.title if instance.lesson else None

    def get_course_title(self, instance: Payments) -> Optional[str]:
        """Возвращает название курса"""
        return instance.course.course_title if instance.course else None

    def get_customer_email(self, instance: Payments) -> Optional[str]:
        """Возвращает email покупателя"""
        return instance.user.email if instance.user else None

    def get_course_owner_email(self, instance: Payments) -> Optional[str]:
        """Возвращает email владельца"""
        if instance.course and instance.course.owner:
            return instance.course.owner.email
        return None

    class Meta:
        model = Payments
        fields = (
            "id",
            "amount",
            "amount_str",
            "payment_date",
            "payment_method",
            "course",
            "course_title",
            "course_owner_email",
            "lesson",
            "customer_email",
        )
        read_only_fields = (
            "user",
            "payment_date",
        )
        write_only_fields = ("amount",)


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
        return instance.created_at.strftime("%d.%M.%Y %H:%m") if instance.created_at else None

    class Meta:
        model = Subscription
        fields = (
            "id",
            "user_email",
            "course_title",
            "is_active",
            "created_at",
        )
