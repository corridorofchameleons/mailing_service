from datetime import datetime, timezone, timedelta

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, TemplateView

from mailing.forms import MessageForm, ClientForm, MailingFormCreate, MailingFormUpdate
from mailing.models import MailingMessage, Client, Mailing, MailingAttempt
from mailing.utils.task_manager import TaskManager


def index(request):
    return render(request, 'mailing/index.html', {'title': 'Главная'})


class MessageListView(ListView):
    model = MailingMessage
    extra_context = {'title': 'Сообщения'}
    paginate_by = 10


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
    paginate_by = 10


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
    paginate_by = 10

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        qs = Mailing.objects.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Рассылки'
        context['object_list'] = Mailing.objects.prefetch_related('clients').all()
        return context


# для постраничного вывода связанных клиентов используется более гибкий вариант: функция
def mailing_detail(request, pk):

    mailing = (Mailing.objects
               .select_related('message')
               .prefetch_related('clients')
               .get(pk=pk))
    paginator = Paginator(mailing.clients.all(), 5)
    # если нет параметра в url, то выводим 1 страницу
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    context = {'title': 'Просмотр рассылки', 'mailing': mailing, 'page': page, 'clients': page.object_list}

    prev_url = request.META.get('HTTP_REFERER')
    context['prev_url'] = prev_url
    return render(request, 'mailing/mailing_detail.html', context)


class MailingPreCreateView(TemplateView):
    template_name = 'mailing/mailing_pre_create.html'


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingFormCreate
    extra_context = {'message_form': MessageForm}

    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        mailing = form.save()
        mailing.save()

        TaskManager.create_task(
            pk=mailing.pk,
            start=mailing.start_time,
            freq=mailing.frequency,
        )

        #  если текущие дата и время больше даты и времени начала
        #  и меньше даты и времени окончания, отправляется внепланово
        if mailing.start_time < datetime.now(timezone(timedelta(hours=3))) and \
                datetime.now(timezone(timedelta(hours=3))).date() <= mailing.finish_time:
            TaskManager.force_exec(mailing.pk)

        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingFormUpdate

    def form_valid(self, form):
        mailing = form.save()
        mailing.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mailing:mailing_detail', kwargs={'pk': self.object.pk})


def stop_mailing(request, pk):
    if request.method == 'POST':
        mailing = Mailing.objects.get(pk=pk)
        mailing.status = 'f'
        mailing.save()

    return redirect(reverse('mailing:mailing_list'))


def restore_mailing(request, pk):
    if request.method == 'POST':
        mailing = Mailing.objects.get(pk=pk)
        mailing.status = 's'
        mailing.save()

    return redirect(reverse('mailing:mailing_list'))


class LogListView(ListView):
    model = MailingAttempt
    paginate_by = 10

    def get_queryset(self):
        mailing_pk = self.request.GET.get('mailing')
        if mailing_pk:
            qs = MailingAttempt.objects.filter(mailing=mailing_pk)
        else:
            qs = MailingAttempt.objects.all()
        return qs
