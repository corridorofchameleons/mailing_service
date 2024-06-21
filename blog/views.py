from django.views.generic import DetailView

from blog.models import Article


class ArticleDetailView(DetailView):
    model = Article

    def get_object(self, queryset=None):
        article = super().get_object()
        article.views += 1
        article.save()
        return article
