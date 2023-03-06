from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_200_OK
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (AdminModeratorAuthorPermission, IsUserAdmin,
                             IsUserAdminOrReadOnly, ReviewsCommentsPermission)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, PostTitleSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitleSerializer, TokenSerializer, UserSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsUserAdminOrReadOnly)
    serializer_class = CategorySerializer
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination


class GenreViewSet(CategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsUserAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return PostTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewsCommentsPermission,
                          permissions.IsAuthenticatedOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ('username',)
    permission_classes = (IsUserAdmin, permissions.IsAuthenticated, )
    lookup_field = 'username'
    lookup_value_regex = r'[\w.@+-]+'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class = LimitOffsetPagination

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def get_patch_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if request.user.is_admin:
                serializer.save()
            else:
                serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)


def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    return send_mail(
        'Код подтверждения от yamdb',
        f'Код подтверждения:{confirmation_code}',
        'admin@admin.ru',
        [user.email],
        fail_silently=False
    )


@api_view(['POST'])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    try:
        user, create = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError as error:
        raise ValidationError(
            ('Ошибка при попытке создать новую запись '
             f'в базе с username={username}, email={email}')
        ) from error
    send_confirmation_code(user)
    return Response(serializer.validated_data, status=HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        token = request.data['confirmation_code']
        check_token = default_token_generator.check_token(user, token)
        if check_token is True:
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        if check_token is False:
            return Response(
                {'message': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'token': f'{str(token)}'},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
