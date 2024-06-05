from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView

from mailing.forms import MessageForm, ClientForm
from mailing.models import MailingMessage, Client, Mailing


def index(request):
    return render(request, 'mailing/index.html')


class MessageListView(ListView):
    model = MailingMessage


class MessageDetailView(DetailView):
    model = MailingMessage

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        prev_url = self.request.META.get('HTTP_REFERER')
        context['prev_url'] = prev_url

        return context


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


class ClientListView(ListView):
    model = Client


class ClientDetailView(DetailView):
    model = Client

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        prev_url = self.request.META.get('HTTP_REFERER')
        context['prev_url'] = prev_url
        return context


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm

    success_url = reverse_lazy('mailing:client_list')


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm

    success_url = reverse_lazy('mailing:client_list')


class ClientDeleteView(DeleteView):
    model = Client

    success_url = reverse_lazy('mailing:client_list')


class MailingListView(ListView):
    model = Mailing


class MailingDetailView(DetailView):
    model = Mailing

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        mailing = Mailing.objects.get(pk=self.kwargs.get('pk'))
        clients = Client.objects.filter(mailings=mailing)
        context['clients'] = clients
        prev_url = self.request.META.get('HTTP_REFERER')
        context['prev_url'] = prev_url
        return context
