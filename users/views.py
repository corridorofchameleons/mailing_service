import os
import secrets

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, ListView

from users.forms import UserRegisterForm, UserUpdateForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:email_sent')
    template_name = 'users/user_form.html'
    extra_context = {'title': 'Регистрация'}

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_urlsafe(32)
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f'http://{host}/users/verification/{token}'

        send_mail(
            subject='SFMailing подтверждение регистрации',
            message=f'Привет, {user.email}!\n\n'
                    f'Для активации перейди по ссылке: {url}\n\n'
                    f'Команда SFMailing',
            from_email=os.getenv('SMTP_USER'),
            recipient_list=[user.email]
        )
        return super().form_valid(form)


class MailSentView(TemplateView):
    template_name = 'users/email_sent.html'


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return render(request, 'users/user_activated.html')


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_update.html'
    success_url = reverse_lazy('mailing:index')
    extra_context = {'title': 'Изменение данных'}

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.request.user.pk)


class UserDeleteView(DeleteView):
    model = User
    success_url = '/'
    template_name = 'users/user_confirm_delete.html'
    extra_context = {'title': 'Удаление аккаунта'}

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.request.user.pk)


class UserListView(PermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    extra_context = {'title': 'Пользователи'}
    paginate_by = 20
    permission_required = ('users.view_user', 'users.can_deactivate_user')
    raise_exception = True

    def get_queryset(self):
        q = ~Q(groups__name__in=['manager']) & Q(is_superuser=False)
        return User.objects.filter(q)


@permission_required('users.can_deactivate_user')
def deactivate_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()

        return redirect(reverse('users:user_list'))
    raise PermissionDenied()


@permission_required('users.can_deactivate_user')
def activate_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save()

        return redirect(reverse('users:user_list'))
    raise PermissionDenied()

