from django.contrib.auth.views import LoginView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetView, \
    PasswordResetCompleteView, LogoutView
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import UserCreateView, MailSentView, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path('register/email_sent', MailSentView.as_view(), name='email_sent'),
    path('register/', UserCreateView.as_view(), name='user_create'),
    path('verification/<str:token>/', email_verification),

    path('login/', LoginView.as_view(
        template_name='users/login.html'
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='users/confirm_password.html',
        success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password_reset/done', PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset/', PasswordResetView.as_view(
        template_name="users/password_reset.html",
        email_template_name="users/reset_email.txt",
        success_url=reverse_lazy("users:password_reset_done")
    ), name='password_reset'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='users/password_confirmed.html'
    ), name='password_reset_complete')
]
