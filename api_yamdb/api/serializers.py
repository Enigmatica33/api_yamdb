from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers, validators

from reviews.models import Title, Genre, Category, Review, Comment

User = get_user_model()

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
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            # 'rating',
            'description',
            'genre',
            'category'
        )

    def validate_year(self, value):
        """Проверка года создания произведения."""
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год создания не может быть больше текущего!',
            )
        return value


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
    title = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
            )
        ]

    get_title(self, obj):
       return get_object_or_404(Title, id=self.kwargs.get('title_id'))


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        'username',
        read_only=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'pub_date')

