import random

from django.conf import settings
from django.core.cache import cache

from blog.models import Article


def get_random_three():
    if settings.CACHE_ENABLED:
        key = 'articles'
        articles = cache.get(key)
        if articles:
            return articles
        articles = random.sample(list(Article.objects.all()), 3)
        cache.set(key, articles, 60)
        return articles
    return random.sample(list(Article.objects.all()), 3)
