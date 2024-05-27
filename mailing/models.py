from django.db import models
from django.utils import timezone

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(max_length=254, unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    patronym = models.CharField(max_length=30, **NULLABLE, verbose_name='Отчество')
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)
    mailing_id = models.ManyToManyField('mailing.Mailing', verbose_name='Рассылка', related_name='clients')

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
    finish_time = models.DateTimeField(verbose_name='Конец рассылки')
    frequency = models.CharField(max_length=1, choices=FREQUENCY, default='d', verbose_name='Периодичность')
    status = models.CharField(max_length=1, choices=STATUS, default=None, **NULLABLE, verbose_name='Статус')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class MailingMessage(models.Model):
    mailing_id = models.OneToOneField('mailing.Mailing', on_delete=models.CASCADE,
                                      verbose_name='Рассылка', related_name='message')
    subject = models.CharField(max_length=100, verbose_name='Тема письма')
    text = models.TextField(verbose_name='Тело письма')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение рассылки'
        verbose_name_plural = 'Сообщения рассылкок'


class MailingAttempt(models.Model):
    mailing_id = models.OneToOneField('mailing.Mailing', on_delete=models.CASCADE,
                                        verbose_name='Рассылка', related_name='attempt')
    latest_attempt = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)
    response = models.TextField(**NULLABLE)

    def __str__(self):
        return f'{self.latest_attempt} {self.status}'

    class Meta:
        ordering = ['latest_attempt']
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
