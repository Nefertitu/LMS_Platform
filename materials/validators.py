import re
from typing import Any

from rest_framework.serializers import ValidationError


class LinkValidator:
    """Класс-валидатор для проверки, что ссылка не ведет на YouTube"""

    def __init__(self, field: str) -> None:
        """Инициализирует валидатор с указанием имени поля для проверки"""
        self.field = field

    def __call__(self, value: dict[str, Any]) -> None:
        """Выполняет проверку ссылки при вызове экземпляра класса"""

        pattern = re.compile(r"^https?://(www\.)?youtube\.com/[^\s]+$")
        search_field = dict(value).get(self.field)
        if search_field and not bool(pattern.match(search_field)):
            raise ValidationError("Материалы должны быть размещены на YouTube")
