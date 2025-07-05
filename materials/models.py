from django.db import models


class Course(models.Model):
    """Модель Курс"""

    title = models.CharField(max_length=200, verbose_name="название курса", help_text="Укажите название курса")
    preview = models.ImageField(
        verbose_name="превью",
        upload_to="materials/preview",
        blank=True,
        null=True,
        help_text="Загрузите изображение",
    )
    description = models.TextField(
        verbose_name="описание",
        blank=True,
        null=True,
        help_text="Введите описание курса",
    )

    def __str__(self) -> str:
        """Строковое отображение модели Курс"""
        return f"Курс: {self.title}"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    """Модель Урок"""

    title = models.CharField(max_length=200, verbose_name="название урока", help_text="Укажите название урока")
    preview = models.ImageField(
        verbose_name="превью(картинка)",
        upload_to="materials/preview",
        blank=True,
        null=True,
        help_text="Загрузите изображение",
    )
    description = models.TextField(verbose_name="описание", blank=True, null=True, help_text="Введите описание урока")
    link = models.URLField(
        max_length=500, verbose_name="ссылка на видео", blank=True, null=True, help_text="Добавьте ссылку на видео"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")

    def __str__(self) -> str:
        """Строковое отображение модели Урок"""
        return f"Урок: {self.title}, курс: {self.course}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
