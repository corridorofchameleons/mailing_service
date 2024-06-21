from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    content = models.TextField(verbose_name='Содержание')
    img = models.ImageField(upload_to='blog/', verbose_name='Изображение', null=True, blank=True)
    views = models.PositiveIntegerField(verbose_name='Количество просмотров', default=0)
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
