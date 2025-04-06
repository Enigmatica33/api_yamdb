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
