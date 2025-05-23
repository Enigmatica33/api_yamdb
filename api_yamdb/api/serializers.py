from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import Http404
from rest_framework import serializers

from reviews.constants import MAX_NAME_LENGTH, MAX_TEXT_LENGTH
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.models import validate_username


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""
    email = serializers.EmailField(max_length=MAX_TEXT_LENGTH, required=True)
    username = serializers.CharField(
        max_length=MAX_NAME_LENGTH,
        required=True,
        validators=[validate_username]
    )

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        user, _ = User.objects.get_or_create(email=email, username=username)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email='from@yamdb.com',
            recipient_list=[email],
            fail_silently=False,
        )
        return user

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        # Если оба существуют, но это разные юзеры — ошибка
        if user_by_email and user_by_username and (
           user_by_email != user_by_username):
            raise serializers.ValidationError({
                'email': 'Адрес уже используется другим пользователем.',
                'username': 'Имя пользователя уже занято другим адресом.'
            })

        # Если только email занят, но не этим username
        if user_by_email and not user_by_username:
            raise serializers.ValidationError({
                'email': 'Адрес уже используется другим пользователем.'
            })

        # Если только username занят, но не этим email
        if user_by_username and not user_by_email:
            raise serializers.ValidationError({
                'username': 'Имя пользователя уже занято другим адресом.'
            })

        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(max_length=MAX_NAME_LENGTH, required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404('Пользователь не найден.')

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Некорректный код подтверждения.'})

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')


class MeSerializer(UserSerializer):
    """Сериализатор Me."""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


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
    rating = serializers.IntegerField(read_only=True, default=None)

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


class TitleReadSerializer(TitleSerializer):
    """Сериализатор модели Title для чтения."""
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)


class TitleWriteSerializer(TitleSerializer):
    """Сериализатор модели Title для записи."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        write_only=True
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_null=False,
        allow_empty=False,
        write_only=True
    )

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""
    author = serializers.SlugRelatedField(
        'username',
        read_only=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = request.user
            if Review.objects.filter(title__id=title_id,
                                     author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment."""
    author = serializers.SlugRelatedField(
        'username',
        read_only=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
