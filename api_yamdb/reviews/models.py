from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year
from users.models import User


class BaseGenreCategory(models.Model):
    name = models.CharField(
        'Название', max_length=settings.NAME_LEN, unique=True)
    slug = models.SlugField(unique=True, verbose_name='URL')

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Genre(BaseGenreCategory):

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(BaseGenreCategory):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(
        'Название произведения', max_length=settings.NAME_LEN,)
    year = models.PositiveSmallIntegerField(
        'Год выпуска', validators=(validate_year,)
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        help_text='Выберите категорию'
    )
    description = models.TextField(
        'Описание произведения',
        help_text='Кратко опишите произведение',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class BaseReviewComment(models.Model):
    text = models.TextField(
        'Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        'Дата',
        db_index=True,
        auto_now_add=True,
    )

    def __str__(self):
        return self.text

    class Meta:
        abstract = True


class Review(BaseReviewComment):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    score = models.IntegerField(
        'Оценка',
        default=0,
        validators=(
            MaxValueValidator(10),
            MinValueValidator(1)
        ),
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title',),
                name='unique_review')
        ]


class Comment(BaseReviewComment):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
