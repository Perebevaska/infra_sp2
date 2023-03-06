from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import validate_me_name


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    ]
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USER_LEN_NAME,
        unique=True,
        help_text=(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, validate_me_name],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.LEN_EMAIL,
        unique=True
    )
    role = models.CharField(
        'Роль',
        max_length=settings.LEN_ROLE,
        choices=ROLE_CHOICES,
        default=USER,
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.USER_LEN_NAME,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USER_LEN_NAME,
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_staff

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
