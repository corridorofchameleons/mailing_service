from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from mailing.apps import MailingConfig
from mailing.views import index, MessageCreateView, MessageListView, MessageUpdateView, MessageDetailView, \
    MessageDeleteView, ClientCreateView, ClientUpdateView, ClientDeleteView, ClientDetailView, ClientListView

app_name = MailingConfig.name

urlpatterns = [
    path('', index, name='index'),

    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>', MessageUpdateView.as_view(), name='message_update'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:pk>', MessageDetailView.as_view(), name='message_detail'),
    path('messages/', MessageListView.as_view(), name='message_list'),

    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/update/<int:pk>', ClientUpdateView.as_view(), name='client_update'),
    path('clients/delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:pk>', ClientDetailView.as_view(), name='client_detail'),
    path('clients/', ClientListView.as_view(), name='client_list'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
