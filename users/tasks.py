import os
from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from users.models import User


@shared_task
def check_last_login_and_block():
    """Блокирует пользователей, которые не заходили более месяца"""

    now = timezone.now()
    time_difference = now - timedelta(days=30)   #(minutes=5)

    users_to_block = User.objects.filter(Q(last_login__lt=time_difference) | Q(last_login__isnull=True), is_active=True, is_superuser=False).values_list("email", flat=True)

    emails_list = list(users_to_block)
    count_users = len(emails_list)

    User.objects.filter(email__in=emails_list).update(is_active=False)

    message = f"Выполнена блокировка {count_users} пользователей: {emails_list}"
    print(message)
    for email in emails_list:
        try:
            send_mail(
                f"Блокировка пользователя",
                f"Уважаемый пользователь (email: {email})!\n"
                f"Ваша учетная запись заблокирована, так как была неактивна в течение 1-го месяца",
                os.getenv("EMAIL_HOST_USER"),
                [email],
                fail_silently=False
                )

            print(f"Отправлено письмо пользователю: {email}")

        except Exception as e:
            print(f"Ошибка: {e}")
    return message
