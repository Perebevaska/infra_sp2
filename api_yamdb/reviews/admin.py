from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from reviews.models import Category, Comment, Genre, Review, Title


class GenreResource(resources.ModelResource):

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug',)


@admin.register(Genre)
class GenreAdmin(ImportExportModelAdmin):
    resource_classes = [GenreResource]
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class CategoryResource(resources.ModelResource):

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug',)


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_classes = [CategoryResource]
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TitleResource(resources.ModelResource):

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category',)


class GenreTitleResource(resources.ModelResource):
    title = Field(attribute='title', column_name='title_id',
                  widget=ForeignKeyWidget(Title))
    genre = Field(attribute='genre', column_name='genre_id',
                  widget=ForeignKeyWidget(Genre))

    class Meta:
        model = Title.genre.through
        columns = ('id', 'genre_id', 'title_id', )


class GenreTitleInline(admin.TabularInline):
    model = Title.genre.through


@admin.register(Title)
class TitleAdmin(ImportExportModelAdmin):
    resource_classes = [TitleResource, GenreTitleResource]
    list_display = ('name', 'year', 'category', 'description',)
    inlines = (GenreTitleInline, )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class ReviewResource(resources.ModelResource):
    title = Field(attribute='title', column_name='title_id',
                  widget=ForeignKeyWidget(Title))

    class Meta:
        model = Review
        columns = ['id', 'title_id', 'text', 'author', 'score', 'pub_date', ]


@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    resource_classes = [ReviewResource]
    list_display = ('title', 'text', 'author', 'pub_date', 'score',)
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentResource(resources.ModelResource):
    review = Field(attribute='review', column_name='review_id',
                   widget=ForeignKeyWidget(Review))

    class Meta:
        model = Comment
        columns = ('id', 'review_id', 'text', 'author', 'pub_date',)


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    resource_classes = [CommentResource]
    list_display = ('review', 'text', 'author', 'pub_date',)
    search_fields = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'
