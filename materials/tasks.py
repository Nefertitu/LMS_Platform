import os

from celery import shared_task
from django.core.mail import send_mail
from django.db import close_old_connections

from materials.models import Subscription


@shared_task
def notify_subscriber(subscription_pk):
    """Отправляет сообщения об обновлении курсов пользователям, подписанным на них"""

    subscription = Subscription.objects.all().get(pk=subscription_pk)

    try:
        send_mail(
            f"Обновление материалов курса '{subscription.course.course_title}'",
            f"Вы пописаны на обновления курса {subscription.course.course_title}",
            os.getenv("EMAIL_HOST_USER"),
            [subscription.user.email],
            fail_silently=False
        )
        for email in subscription.user.email:
            print(f"Найдены изменения курса, отправлено сообщение пользователю {email}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        close_old_connections()
