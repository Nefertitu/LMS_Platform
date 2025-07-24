import os

from celery import shared_task
from django.core.mail import send_mail
from django.db import close_old_connections

from materials.models import Subscription


@shared_task
def notify_subscriber(subscription_pk: int) -> None:
    """Отправляет сообщения об обновлении курсов пользователям, подписанным на них"""

    try:
        subscription = Subscription.objects.all().get(pk=subscription_pk)

        if not subscription.user or not subscription.user.email:
            raise ValueError("У подписки отсутствует пользователь или email")

        if not subscription.course:
            raise ValueError("У подписки отсутствует курс")

        send_mail(
            f"Обновление материалов курса '{subscription.course.course_title}'",
            f"Вы пописаны на обновления курса {subscription.course.course_title}",
            os.getenv("EMAIL_HOST_USER"),
            [subscription.user.email],
            fail_silently=False,
        )
        print(f"Найдены изменения курса, отправлено сообщение пользователю {subscription.user.email}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        close_old_connections()
