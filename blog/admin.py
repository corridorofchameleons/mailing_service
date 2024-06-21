from django.contrib import admin

from blog.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title']
    fields = ['title', 'content', 'img']

    class Meta:
        order_by = ['-published_at']
