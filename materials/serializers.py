from typing import Optional

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from materials.models import Course, Lesson, Subscription
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
        fields = ("id", "course_title", "preview", "description", "owner", "is_subscribed", "lessons", "lessons_count", "price")


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
        return instance.created_at.strftime("%d.%m.%Y %H:%M") if instance.created_at else None

    class Meta:
        model = Subscription
        fields = (
            "id",
            "user_email",
            "course_title",
            "is_active",
            "created_at",
        )
