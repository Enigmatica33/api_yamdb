from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg
from rest_framework import serializers
from rest_framework import validators as rf_validators
from django.core import validators
import re

from reviews.models import Title, Genre, Category, Review, User, Comment
from reviews.models import MAX_TEXT_LENGTH, MAX_NAME_LENGTH


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Пользователь 'me' запрещён.")
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                "Имя может содержать буквы, цифры и символы @/./+/-/_."
            )
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if User.objects.filter(email=email, username=username).exists():
            return data

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Адрес уже используется другим пользователем."})

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "Имя пользователя уже занято другим адресом."})
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=MAX_TEXT_LENGTH,
        validators=[rf_validators.UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        max_length=MAX_NAME_LENGTH,
        validators=[
            validators.RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message="Имя может содержать буквы, цифры и символы @/./+/-/_."
            ),
            rf_validators.UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

    def validate_email(self, value):
        if len(value) > MAX_TEXT_LENGTH:
            raise serializers.ValidationError(
                f"Адрес не должен быть больше {MAX_TEXT_LENGTH} симв.")
        return value

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Пользователь 'me' запрещён.")
        return value


class MeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    username = serializers.CharField(
        max_length=MAX_NAME_LENGTH,
        validators=[
            validators.RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message="Имя может содержать буквы, цифры и символы @/./+/-/_."
            )
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Пользователь 'me' запрещён.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False,
        write_only=True
    )

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        write_only=True
    )

    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )

    def validate_year(self, value):
        """Проверка года создания произведения."""
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год создания не может быть больше текущего!',
            )
        return value

    def get_rating(self, object):
        rating = object.reviews.aggregate(Avg('score'))['score__avg']
        return rating

    def get_category_display(self, obj):
        if obj.category:
            return {'name': obj.category.name, 'slug': obj.category.slug}
        return None

    def get_genre_display(self, obj):
        return [{'name': genre.name,
                 'slug': genre.slug} for genre in obj.genre.all()]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('category', None)
        representation.pop('genre', None)
        representation['category'] = self.get_category_display(instance)
        representation['genre'] = self.get_genre_display(instance)
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        'username',
        read_only=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())

    score = serializers.IntegerField(
        max_value=10,
        min_value=1
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        read_only_fields = ('title',)

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            title = get_object_or_404(Title, id=title_id)
            author = request.user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        'username',
        read_only=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    review = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        read_only_fields = ('pub_date',)

    def validate(self, data):
        if 'review' not in data:
            review_id = self.context['view'].kwargs.get('review_id')
            data['review'] = get_object_or_404(Review, id=review_id)
        return data
