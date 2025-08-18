from django.db import models

from config import settings


class Course(models.Model):
    """Модель Курс"""

    course_title = models.CharField(
        max_length=200, verbose_name="Название курса", blank=False, null=False, help_text="Укажите название курса"
    )
    preview = models.ImageField(
        verbose_name="Превью",
        upload_to="materials/preview",
        blank=True,
        null=True,
        help_text="Загрузите изображение",
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
        help_text="Введите описание курса",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Владелец",
        help_text="Укажите владельца курса",
        related_name="owner_courses",
    )
    price = models.DecimalField(
        verbose_name="Стоимость курса",
        max_digits=20,
        decimal_places=2,
        blank=False,
        null=False,
        help_text="Укажите стоимость курса",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата и время создания курса",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата и время обновления курса",
        auto_now=True,
    )

    def __str__(self) -> str:
        """Строковое отображение модели Курс"""
        return f"Курс: {self.course_title}"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["id"]


class Lesson(models.Model):
    """Модель Урок"""

    title = models.CharField(max_length=200, verbose_name="название урока", help_text="Укажите название урока")
    preview = models.ImageField(
        verbose_name="Превью(картинка)",
        upload_to="materials/preview",
        blank=True,
        null=True,
        help_text="Загрузите изображение",
    )
    description = models.TextField(verbose_name="Описание", blank=True, null=True, help_text="Введите описание урока")
    link = models.URLField(
        max_length=500, verbose_name="Ссылка на видео", blank=True, null=True, help_text="Добавьте ссылку на видео"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс", blank=True, null=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите владельца урока",
        related_name="owner_lessons",
    )
    price = models.DecimalField(
        verbose_name="Стоимость урока",
        max_digits=20,
        decimal_places=2,
        blank=False,
        null=False,
        help_text="Укажите стоимость урока",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата и время создания урока",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="Дата и время обновления урока",
        auto_now=True,
    )

    def __str__(self) -> str:
        """Строковое отображение модели Урок"""
        return f"Урок: {self.title}, курс: {self.course}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["id"]


class Subscription(models.Model):
    """Модель Подписка"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        related_name="user_subscriptions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        help_text="Курс по подписке",
        blank=False,
        null=False,
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна", help_text="Отметка об активности подписки")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self) -> str:
        """Строковое отображение модели Подписка"""
        assert self.user is not None
        status = "активна" if self.is_active else "неактивна"
        return f"Подписка пользователя {self.user.email} на курс {self.course.course_title} {status}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course")
