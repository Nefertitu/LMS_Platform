from typing import Any, Type

from django.conf import settings
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from users.models import User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(
    sender: Type[Model], instance: User, created: bool = False, **kwargs: Any
) -> None:
    """Сигнал для автоматического создания токена при создании нового пользователя"""
    if created:
        Token.objects.create(user=instance)
