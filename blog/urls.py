from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from blog.apps import BlogConfig
from blog.views import ArticleDetailView

app_name = BlogConfig.name

urlpatterns = [
    path('articles/<int:pk>', ArticleDetailView.as_view(), name='article_detail')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
