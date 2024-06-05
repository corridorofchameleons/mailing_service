from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from mailing.apps import MailingConfig
from mailing.views import index, MessageCreateView, MessageListView, MessageUpdateView, MessageDetailView, \
    MessageDeleteView

app_name = MailingConfig.name

urlpatterns = [
    path('', index, name='index'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>', MessageUpdateView.as_view(), name='message_update'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:pk>', MessageDetailView.as_view(), name='message_detail'),
    path('messages/', MessageListView.as_view(), name='message_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
