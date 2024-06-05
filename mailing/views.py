from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView

from mailing.forms import MessageForm
from mailing.models import MailingMessage


def index(request):
    return render(request, 'mailing/index.html')


class MessageListView(ListView):
    model = MailingMessage


class MessageDetailView(DetailView):
    model = MailingMessage


class MessageCreateView(CreateView):
    model = MailingMessage
    form_class = MessageForm

    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(UpdateView):
    model = MailingMessage
    form_class = MessageForm

    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(DeleteView):
    model = MailingMessage

    success_url = reverse_lazy('mailing:message_list')