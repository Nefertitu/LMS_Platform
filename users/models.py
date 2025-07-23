from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from config import settings


class User(AbstractUser):
    """Модель пользователя с кастомными полями.
    Заменяет стандартный `username` на `email`
    в качестве основного идентификатора."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Укажите email",
    )
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name="Телефон", help_text="Укажите телефон")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Город", help_text="Укажите город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите свой аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        """Строковое представление объекта пользователя"""
        return f"{self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    """Модель Платеж"""

    CASH = "cash"
    TRANSFER = "transfer"

    PAY_METHOD_CHOICE = [(CASH, "Наличные"), (TRANSFER, "Перевод на счет")]

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает оплаты"),
        (STATUS_PAID, "Оплачено"),
        (STATUS_CANCELED, "Отменено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        blank=True,
        null=True,
        help_text="Пользователь",
    )

    lesson = models.ForeignKey(
        "materials.Lesson",
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="Оплаченный урок",
        blank=True,
        null=True,
    )
    course = models.ForeignKey(
        "materials.Course",
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="Оплаченный курс",
        blank=True,
        null=True,
    )

    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии",
        help_text="Укажите ID сессии",
    )
    link = models.URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
        help_text="Ссылка на оплату",
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PAY_METHOD_CHOICE,
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
        default=TRANSFER,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_date = models.DateTimeField(
        verbose_name="Дата оплаты",
        default=timezone.now,
    )

    def __str__(self) -> str:
        """Строковое отображение платежа"""
        if self.course and hasattr(self.course, "price"):
            return str(self.course.price)
        elif self.lesson and hasattr(self.lesson, "price"):
            return str(self.lesson.price)
        else:
            return "У продукта не указана цена"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-id"]
