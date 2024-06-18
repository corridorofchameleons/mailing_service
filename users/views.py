import os
import secrets

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, FormView

from users.forms import UserRegisterForm, PasswordResetForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:mail_sent')
    template_name = 'users/user_form.html'

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
            message=f'Привет, {user.email}\n\n!'
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


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = 'users/password_reset.html'
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')

        url = reverse('users:password_reset')
        # не хрестоматийный способ, но пока пусть так
        url += secrets.token_urlsafe(32)

        try:
            user = get_object_or_404(User, email=email)
        except:
            return redirect(reverse('users:reset_password'))
        else:
            send_mail(
                subject='Запрос на сброс пароля',
                message=f'Привет, {user.email}!\n\n'
                        f'Для сброса пароля пройди по ссылке:\n'
                        f'{url}\n\n'
                        f'SF Mailing',
                from_email=os.getenv('SMTP_USER'),
                recipient_list=[user.email]
            )
            return super().form_valid(form)

