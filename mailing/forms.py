from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone

from mailing.models import MailingMessage, Client, Mailing


class MessageForm(forms.ModelForm):
    class Meta:
        model = MailingMessage
        exclude = ['user']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user']


class MailingFormCreate(forms.ModelForm):

    # переопределяем init для отсеивания чужих клиентов и писем
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields.get('clients').queryset = Client.objects.filter(user=self.user)
        self.fields.get('message').queryset = MailingMessage.objects.filter(user=self.user)

    name = forms.CharField(label='Название рассылки')
    start_time = forms.SplitDateTimeField(label='Начало рассылки', initial=timezone.now,
                                          widget=forms.SplitDateTimeWidget(date_format="%d/%m/%Y",
                                                                           date_attrs={"type": "date"}))
    finish_time = forms.DateField(label='Конец рассылки',
                                  widget=forms.DateInput(format="%d/%m/%Y", attrs={"type": "date"}),
                                  help_text='Рассылка будет осуществляться в заданное время до \
                                    последнего дня включительно')
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(),
                                             label='Клиенты',
                                             widget=forms.widgets.CheckboxSelectMultiple())
    frequency = forms.ChoiceField(label='Периодичность',
                                  widget=forms.RadioSelect,
                                  choices=Mailing.FREQUENCY)

    class Meta:
        model = Mailing
        fields = ('name', 'message', 'start_time', 'finish_time', 'frequency', 'clients')


class MailingFormUpdate(MailingFormCreate):
    start_time = forms.DateTimeField(disabled=True, label='Начало рассылки')
    frequency = forms.ChoiceField(disabled=True,
                                  label='Периодичность',
                                  widget=forms.RadioSelect,
                                  choices=Mailing.FREQUENCY,
                                  help_text='Для изменения периодичности необходимо создать новую рассылку')
