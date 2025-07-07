from django.db import models

from users.models import User


class Course(models.Model):
    """Модель Курс"""

    course_title = models.CharField(max_length=200, verbose_name="название курса", help_text="Укажите название курса")
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
        return f"Курс: {self.course_title}"

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


class Payments(models.Model):
    """Класс Платежи"""

    CASH = "Наличные"
    TRANSFER = "Перевод на счет"

    PAY_METHOD_CHOICE = [(CASH, "Наличные"), (TRANSFER, "Перевод на счет")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_payments", help_text="Пользователь")
    payment_date = models.DateTimeField(
        verbose_name="дата оплаты", blank=True, null=True, help_text="Укажите дату оплаты"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="lesson_payments",
        help_text="Оплаченный урок",
        blank=True,
        null=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_payments",
        help_text="Оплаченный курс",
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        verbose_name="сумма оплаты",
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Укажите сумму оплаты",
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PAY_METHOD_CHOICE,
        verbose_name="способ оплаты",
        help_text="Выберите способ оплаты",
        default=TRANSFER,
    )

    def __str__(self) -> str:
        """Строковое отображение платежей"""
        return f"{self.course} - {self.lesson} - {self.payment_date} - {self.amount}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["payment_date", "amount"]
