from django.db import models
from django.utils import timezone

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(max_length=254, unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    patronym = models.CharField(max_length=30, **NULLABLE, verbose_name='Отчество')
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronym}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Mailing(models.Model):
    FREQUENCY = (
        ('d', 'ежедневно'),
        ('w', 'еженедельно'),
        ('m', 'ежемесячно'),
    )

    STATUS = (
        ('c', 'создана'),
        ('s', 'запущена'),
        ('f', 'завершена')
    )

    name = models.CharField(max_length=100, verbose_name='Наименование')
    start_time = models.DateTimeField(default=timezone.now, verbose_name='Начало рассылки')
    finish_time = models.DateField(verbose_name='Последний день')
    frequency = models.CharField(max_length=1, choices=FREQUENCY, default='d', verbose_name='Периодичность')
    status = models.CharField(max_length=1, choices=STATUS, default='c', verbose_name='Статус')
    created_at = models.DateField(auto_now=True, verbose_name='Дата создания')

    # для возможности повторного использования сообщения
    message = models.ForeignKey('mailing.MailingMessage', on_delete=models.PROTECT, verbose_name='Сообщение',
                                   related_name='mailings')
    # для возможности повторного использования клиентов
    clients = models.ManyToManyField('mailing.Client', verbose_name='Клиенты', related_name='mailings')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at', '-start_time']


class MailingMessage(models.Model):
    subject = models.CharField(max_length=100, verbose_name='Тема письма')
    text = models.TextField(verbose_name='Тело письма')
    created_at = models.DateField(auto_now=True, verbose_name='Дата создания')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение рассылки'
        verbose_name_plural = 'Сообщения рассылкок'
        ordering = ['-created_at']


class MailingAttempt(models.Model):
    mailing_id = models.OneToOneField('mailing.Mailing', on_delete=models.CASCADE,
                                        verbose_name='Рассылка', related_name='attempt')
    latest_attempt = models.DateTimeField(default=None, **NULLABLE, verbose_name='Последняя попытка')
    status = models.BooleanField(default=False, verbose_name='Результат')
    response = models.TextField(**NULLABLE, verbose_name='Сообщение')

    def __str__(self):
        return f'{self.latest_attempt} {self.status}'

    class Meta:
        ordering = ['-latest_attempt']
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
