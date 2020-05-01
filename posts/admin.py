from django.contrib import admin

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "text", "pub_date", "author") 
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",) 
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class PostGroup(admin.ModelAdmin):
    list_display = ("title", "slug", "description")


class PostComment(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, PostGroup)
admin.site.register(Comment, PostComment)
