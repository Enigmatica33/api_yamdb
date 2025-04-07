from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import TextChoices

from reviews.constants import (
    MAX_NAME_LENGTH,
    MAX_ROLE_LENGTH,
    MAX_SCORE,
    MIN_SCORE,
    MAX_TITLE_LENGTH,
    MAX_TEXT_LENGTH,
)
from reviews.validators import validate_year, validate_username


class UserRole(TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    """Модель Пользователя."""
    username = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Пользователь',
        validators=[validate_username]
    )
    email = models.EmailField(
        max_length=MAX_TEXT_LENGTH,
        null=False,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=True,
        verbose_name='Фамилия'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=MAX_ROLE_LENGTH,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == 'admin'
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR


class CategoryGenre(models.Model):
    """Абстрактная модель для Категории и Жанра."""
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug',
        help_text=(
            'Идентификатор для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        abstract = True
        ordering = ('name',)


class Category(CategoryGenre):
    """Модель Категории."""
    class Meta:
        verbose_name = 'Категория произведений'
        verbose_name_plural = 'Категории произведений'

    def __str__(self):
        return self.name


class Genre(CategoryGenre):
    """Модель Жанра."""
    class Meta:
        verbose_name = 'Жанр произведений'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель Произведения."""
    name = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=[
            validate_year,
        ],
        verbose_name='Год создания'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        through='Title_Genre',
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
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title_Genre(models.Model):
    """Связь жанра и Произведения."""
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Жанр',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('genre', 'title'),
                name='unique_genre_title',
            ),
        )

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Модель Отзыва."""
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    score = models.SmallIntegerField(
        validators=[
            MaxValueValidator(MAX_SCORE),
            MinValueValidator(MIN_SCORE)
        ],
        verbose_name='Оценка'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        unique_together = ('title', 'author')
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MAX_TITLE_LENGTH]


class Comment(models.Model):
    """Модель Комментария."""
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MAX_TITLE_LENGTH]
