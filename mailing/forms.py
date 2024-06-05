from django.forms import models
from mailing.models import MailingMessage, Client


class MessageForm(models.ModelForm):
    class Meta:
        model = MailingMessage
        fields = '__all__'


class ClientForm(models.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
