from django.contrib import admin

from materials.models import Course, Lesson


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
