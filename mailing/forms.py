from django import forms
from django.utils import timezone

from mailing.models import MailingMessage, Client, Mailing


class MessageForm(forms.ModelForm):
    class Meta:
        model = MailingMessage
        fields = '__all__'


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class MailingFormCreate(forms.ModelForm):
    name = forms.CharField(label='Название рассылки')
    start_time = forms.DateTimeField(label='Начало рассылки', initial=timezone.now)
    finish_time = forms.DateTimeField(label='Конец рассылки')
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all())

    class Meta:
        model = Mailing
        fields = ('name', 'message', 'start_time', 'finish_time', 'frequency', 'clients')


class MailingFormUpdate(MailingFormCreate):
    start_time = forms.DateTimeField(disabled=True)

