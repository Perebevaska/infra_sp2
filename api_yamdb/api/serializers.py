from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import BadRequest
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import validate_year
from users.models import User
from users.validators import validate_me_name


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True,)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.reviews.aggregate(Avg('score')).get('score__avg')

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title


class PostTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True)
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())
    year = serializers.IntegerField(validators=(validate_year,))

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs["title_id"])
        review = title.reviews.filter(
            author_id=self.context['request'].user.pk)
        if self.context['request'].method == 'POST' and review:
            raise BadRequest(
                'Можно оставить только один отзыв к одному произведению'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'bio', 'role']


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, max_length=settings.LEN_EMAIL, )
    username = serializers.CharField(
        max_length=settings.USER_LEN_NAME,
        required=True,
        validators=[UnicodeUsernameValidator(), validate_me_name],
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
