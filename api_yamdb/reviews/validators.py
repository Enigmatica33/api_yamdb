import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверка года создания произведения."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            'Год создания не может быть больше текущего!',
        )
    return value


def validate_username(value):
    """Проверка имени пользователя."""
    if value.lower() == 'me':
        raise ValidationError('Имя <me> запрещено.')
    if not re.fullmatch(r'^[\w.@+-]+$', value):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы. '
            'Разрешены только буквы, цифры и символы @/./+/-/_'
        )