from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


MAX_TITLE_LENGTH = 256
MIN_YEAR = -3000


class Category(models.Model):
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug категории',
        help_text=(
            "Идентификатор категории для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "Категория произведений"
        verbose_name_plural = "Категории произведений"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug жанра',
        help_text=(
            "Идентификатор жанра для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),

    )

    class Meta:
        verbose_name = "Жанр произведений"
        verbose_name_plural = "Жанры произведений"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(timezone.now().year),
            MinValueValidator(MIN_YEAR)
        ],
        verbose_name='Год создания'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        default_related_name = 'titles'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    title = models.ForeingKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    author = models.ForeingKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        auto_add_now=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "Отзывы"
        default_related_name = 'reviews'
        unique_together = ('title', 'author')

    def __str__(self):
        return self.text[:20]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    title = models.ForeingKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    review = models.ForeingKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    author = models.ForeingKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        auto_add_now=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:20]


