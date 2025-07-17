from django.contrib import admin

from users.models import Payment, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование пользователей. Позволяет управлять
    пользователями, с возможностью фильтрации и поиска."""

    list_display = (
        "id",
        "email",
        "phone",
    )
    list_filter = ("email",)
    search_fields = (
        "email",
        "phone",
    )

    @admin.register(Payment)
    class PaymentAdmin(admin.ModelAdmin):
        """Администрирование stripe-платежей. Позволяет управлять
        платежами, с возможностью фильтрации и поиска."""

        list_display = (
            "id",
            "user",
            "lesson",
            "course",
        )
        list_filter = ("id",)
        search_fields = ("lesson", "course", "user")
