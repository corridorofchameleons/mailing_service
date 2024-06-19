import os
import secrets

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView

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