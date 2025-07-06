from django.contrib import admin

from materials.models import Course, Lesson, Payments


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Администрирование курсов. Позволяет управлять
    курсами, с возможностью фильтрации и поиска."""

    list_display = (
        "id",
        "title",
        "description",
    )
    list_filter = ("title",)
    search_fields = ("title",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Администрирование уроков. Позволяет управлять
    уроками, с возможностью фильтрации и поиска."""

    list_display = ("id", "title", "description", "course")
    list_filter = ("title", "course")
    search_fields = ("title", "course")


@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    """Администрирование платежей. Позволяет управлять
    платежами, с возможностью фильтрации и поиска."""

    list_display = ("id", "user", "lesson", "course", "payment_date", "amount")
    list_filter = ("payment_date", "amount")
    search_fields = ("lesson", "course", "user")
