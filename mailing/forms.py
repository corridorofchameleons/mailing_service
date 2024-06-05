from django.forms import models
from mailing.models import MailingMessage


class MessageForm(models.ModelForm):
    class Meta:
        model = MailingMessage
        fields = '__all__'
