from rest_framework.exceptions import ValidationError


def validate_lowercase(value: str) -> None:
    if not value.islower():
        raise ValidationError('Заглавные буквы запрещены.')
