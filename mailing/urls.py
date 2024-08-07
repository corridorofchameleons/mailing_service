from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.cache import cache_page

from mailing.apps import MailingConfig
from mailing.views import IndexView, MessageCreateView, MessageListView, MessageUpdateView, MessageDetailView, \
    MessageDeleteView, ClientCreateView, ClientUpdateView, ClientDeleteView, ClientDetailView, ClientListView, \
    MailingListView, MailingCreateView, MailingPreCreateView, MailingUpdateView, stop_mailing, \
    restore_mailing, LogListView, mailing_detail, terminate_mailing

app_name = MailingConfig.name

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

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

    path('mailings/pre_create/', MailingPreCreateView.as_view(), name='mailing_pre_create'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/update/<int:pk>', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/terminate/<int:pk>/', terminate_mailing, name='mailing_terminate'),
    path('mailings/stop/<int:pk>', stop_mailing, name='mailing_stop'),
    path('mailings/restore/<int:pk>', restore_mailing, name='mailing_restore'),
    path('mailings/<int:pk>', mailing_detail, name='mailing_detail'),
    path('mailings/', MailingListView.as_view(), name='mailing_list'),

    path('logs/', LogListView.as_view(), name='attempt_list'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
