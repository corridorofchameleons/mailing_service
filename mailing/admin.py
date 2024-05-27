from django.contrib import admin

from mailing.models import Mailing, MailingAttempt, MailingMessage, Client


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'start_time', 'finish_time', 'frequency', 'status', 'message', 'clients_list']
    fields = ['name', 'start_time', 'finish_time', 'frequency', 'message', 'clients']

    def clients_list(self, obj):
        result = []
        for client in obj.clients.all():
            result.append(f'{client.first_name} {client.last_name}')
        return ', '.join(result)


@admin.register(MailingMessage)
class MailingMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'text', 'mailing_list']

    def mailing_list(self, obj):
        result = []
        for mailing in obj.mailings.all():
            result.append(mailing.name)
        return ', '.join(result)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'patronym', 'comment']


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ['mailing_id', 'latest_attempt', 'status', 'response']
    readonly_fields = ['mailing_id', 'latest_attempt', 'status', 'response']
