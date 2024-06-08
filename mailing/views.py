from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, TemplateView

from mailing.forms import MessageForm, ClientForm, MailingFormCreate, MailingFormUpdate
from mailing.models import MailingMessage, Client, Mailing

from django.db import connection


def index(request):
    return render(request, 'mailing/index.html', {'title': 'Главная'})


class MessageListView(ListView):
    model = MailingMessage
    extra_context = {'title': 'Сообщения'}


class MessageDetailView(DetailView):
    model = MailingMessage
    self_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        obj = (MailingMessage.objects
               .prefetch_related('mailings')
               .get(pk=self.kwargs.get('pk')))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        prev_url = self.request.META.get('HTTP_REFERER')
        context['prev_url'] = prev_url
        context['title'] = 'Просмотр сообщения'

        return context


class MessageCreateView(CreateView):
    model = MailingMessage
    form_class = MessageForm
    extra_context = {'title': 'Создание сообщения'}
    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(UpdateView):
    model = MailingMessage
    form_class = MessageForm
    extra_context = {'title': 'Изменение сообщения'}

    def get_success_url(self):
        return reverse('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(DeleteView):
    model = MailingMessage

    success_url = reverse_lazy('mailing:message_list')


class ClientListView(ListView):
    model = Client
    extra_context = {'title': 'Клиенты'}


class ClientDetailView(DetailView):
    model = Client

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        prev_url = self.request.META.get('HTTP_REFERER')
        context['title'] = 'Просмотр клиента'
        if not prev_url.endswith(reverse('mailing:client_update', kwargs={'pk': self.object.pk})):
            context['prev_url'] = prev_url
        else:
            context['prev_url'] = reverse('mailing:client_list')
        return context


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    extra_context = {'title': 'Создание клиента'}
    success_url = reverse_lazy('mailing:client_list')


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    extra_context = {'title': 'Изменение клиента'}

    def get_success_url(self):
        return reverse('mailing:client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(DeleteView):
    model = Client

    success_url = reverse_lazy('mailing:client_list')


class MailingListView(ListView):
    model = Mailing

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        qs = Mailing.objects.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Рассылки'
        context['object_list'] = Mailing.objects.prefetch_related('clients').all()
        return context


class MailingDetailView(DetailView):
    model = Mailing
    extra_context = {'title': 'Просмотр рассылки'}

    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        obj = (Mailing.objects
               .prefetch_related('clients')
               .select_related('message')
               .get(pk=self.kwargs.get('pk')))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        prev_url = self.request.META.get('HTTP_REFERER')
        context['prev_url'] = prev_url
        return context


class MailingPreCreateView(TemplateView):
    template_name = 'mailing/mailing_pre_create.html'


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingFormCreate
    extra_context = {'message_form': MessageForm}

    success_url = reverse_lazy('mailing:mailing_list')


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingFormUpdate

    def get_success_url(self):
        return reverse('mailing:mailing_detail', kwargs={'pk': self.object.pk})
