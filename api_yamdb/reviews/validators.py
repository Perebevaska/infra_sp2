from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(year):
    if year > timezone.datetime.today().year:
        raise ValidationError(f'Некорректный год {year}')
    return year
