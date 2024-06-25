from datetime import datetime, timezone, timedelta

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, TemplateView

from mailing.forms import MessageForm, ClientForm, MailingFormCreate, MailingFormUpdate
from mailing.models import MailingMessage, Client, Mailing, MailingAttempt
from mailing.utils.cache_utils import get_random_three
from mailing.utils.task_manager import TaskManager


manager_groups = ['manager', 'content manager']


class IndexView(TemplateView):
    template_name = 'mailing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 3 случайные статьи
        context['articles'] = get_random_three()
        # рассылок всего
        context['mailings_num'] = Mailing.objects.all().count()
        # рассылок не в статусе 'завершена'
        context['mailings_active_num'] = Mailing.objects.filter(status__in=['c', 's']).count()
        # количество уникальных клиентов (почт жертв рассылкок)
        context['clients_num'] = Client.objects.distinct('email').count()

        context['title'] = 'Главная'
        return context


class MessageListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = MailingMessage
    extra_context = {'title': 'Сообщения'}
    paginate_by = 10
    raise_exception = True

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()

    def get_queryset(self):
        user = self.request.user
        return MailingMessage.objects.filter(user=user)


class MessageDetailView(UserPassesTestMixin, DetailView):
    model = MailingMessage
    self_url_kwarg = 'pk'

    def test_func(self):
        return self.request.user == self.get_object().user

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


class MessageCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = MailingMessage
    form_class = MessageForm
    extra_context = {'title': 'Создание сообщения'}
    success_url = reverse_lazy('mailing:message_list')

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()

    def form_valid(self, form):
        message = form.save()
        message.user = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(UserPassesTestMixin, UpdateView):
    model = MailingMessage
    form_class = MessageForm
    extra_context = {'title': 'Изменение сообщения'}

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        return reverse('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(UserPassesTestMixin, DeleteView):
    model = MailingMessage
    extra_context = {'title': 'Удаление сообщения'}
    success_url = reverse_lazy('mailing:message_list')

    def test_func(self):
        return self.request.user == self.get_object().user


class ClientListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = Client
    extra_context = {'title': 'Клиенты'}
    paginate_by = 10
    raise_exception = True

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()

    def get_queryset(self):
        user = self.request.user
        return Client.objects.filter(user=user)


class ClientDetailView(UserPassesTestMixin, DetailView):
    model = Client

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        prev_url = self.request.META.get('HTTP_REFERER')
        context['title'] = 'Просмотр клиента'
        if not prev_url.endswith(reverse('mailing:client_update', kwargs={'pk': self.object.pk})):
            context['prev_url'] = prev_url
        else:
            context['prev_url'] = reverse('mailing:client_list')
        return context


class ClientCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    extra_context = {'title': 'Создание клиента'}
    success_url = reverse_lazy('mailing:client_list')

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()

    def form_valid(self, form):
        client = form.save()
        client.user = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm
    extra_context = {'title': 'Изменение клиента'}

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        return reverse('mailing:client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(UserPassesTestMixin, DeleteView):
    model = Client
    extra_context = {'title': 'Удаление клиента'}
    success_url = reverse_lazy('mailing:client_list')

    def test_func(self):
        return self.request.user == self.get_object().user


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    paginate_by = 10

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        user = self.request.user
        if user.has_perm('mailing.view_mailing'):
            qs = Mailing.objects.all()
        else:
            qs = Mailing.objects.filter(name__icontains=search, user=user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Рассылки'
        context['object_list'] = Mailing.objects.prefetch_related('clients').all()
        return context


# для постраничного вывода связанных клиентов используется более гибкий вариант: функция
def mailing_detail(request, pk):
    user = Mailing.objects.get(pk=pk).user
    if user == request.user or request.user.has_perm('mailing.view_mailing'):
        mailing = (Mailing.objects
                   .select_related('message')
                   .prefetch_related('clients')
                   .get(pk=pk))
        paginator = Paginator(mailing.clients.all().order_by('last_name'), 5)
        # если нет параметра в url, то выводим 1 страницу
        page_num = request.GET.get('page', 1)
        page = paginator.get_page(page_num)

        prev_url = request.META.get('HTTP_REFERER')

        mailing_stopped = mailing.status in ('f', 't')
        mailing_paused = mailing.status == 'p'
        mailing_started = mailing.status in ('c', 's')

        context = {
            'title': 'Просмотр рассылки',
            'mailing': mailing,
            'page': page,
            'clients': page.object_list,
            'prev_url': prev_url,

            'mailing_stopped': mailing_stopped,
            'mailing_started': mailing_started,
            'mailing_paused': mailing_paused,
        }
        return render(request, 'mailing/mailing_detail.html', context)
    raise PermissionDenied()


class MailingPreCreateView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = 'mailing/mailing_pre_create.html'
    extra_context = {'title': 'Создание рассылки'}

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()


class MailingCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingFormCreate
    extra_context = {'message_form': MessageForm, 'title': 'Создание рассылки'}
    success_url = reverse_lazy('mailing:mailing_list')

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()

    def get_form_kwargs(self):
        kwargs = super(MailingCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        mailing = form.save()
        mailing.user = self.request.user
        mailing.save()

        # Создает скрипт для crontab
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


class MailingUpdateView(UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingFormUpdate
    extra_context = {'title': 'Изменение рассылки'}

    def get_form_kwargs(self):
        kwargs = super(MailingUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        return self.request.user == self.get_object().user

    def form_valid(self, form):
        mailing = form.save()
        mailing.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mailing:mailing_detail', kwargs={'pk': self.object.pk})


def stop_mailing(request, pk):
    '''
    Останавливает рассылку по команде пользователя.
    работает только через POST
    '''
    if request.method == 'POST':
        user = Mailing.objects.get(pk=pk).user
        if user == request.user:
            mailing = Mailing.objects.get(pk=pk)
            mailing.status = 'p'
            mailing.save()
            return redirect(reverse('mailing:mailing_detail', kwargs={'pk': mailing.pk}))
        raise PermissionDenied()
    raise Http404


def restore_mailing(request, pk):
    '''
    Возобновляет рассылку по команде пользователя.
    работает только через POST
    '''
    if request.method == 'POST':
        user = Mailing.objects.get(pk=pk).user
        if user == request.user:
            mailing = Mailing.objects.get(pk=pk)
            mailing.status = 's'
            mailing.save()
            return redirect(reverse('mailing:mailing_detail', kwargs={'pk': mailing.pk}))
        raise PermissionDenied()
    raise Http404


@permission_required('mailing.can_stop_mailing')
def terminate_mailing(request, pk):
    '''
    Останавливает рассылку по команде менеджера.
    Пользователь возобновить уже не сможет.
    работает только через POST
    '''
    if request.method == 'POST':
        mailing = Mailing.objects.get(pk=pk)
        mailing.status = 't'
        mailing.stopped_by_manager = True
        mailing.save()

        return redirect(reverse('mailing:mailing_detail', kwargs={'pk': mailing.pk}))
    raise Http404


class LogListView(UserPassesTestMixin, ListView):
    model = MailingAttempt
    paginate_by = 10
    extra_context = {'title': 'Отчеты по рассылкам'}

    def test_func(self):
        return not self.request.user.groups.filter(name__in=manager_groups).exists()

    def get_queryset(self):
        mailing_pk = self.request.GET.get('mailing')
        qs = MailingAttempt.objects.filter(mailing__user=self.request.user)
        if mailing_pk:
            qs = qs.filter(mailing=mailing_pk)
        return qs
