# Generated by Django 5.0.6 on 2024-06-25 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0026_remove_mailing_stopped_by_manager_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailing',
            options={'ordering': ('-start_time',), 'permissions': [('can_stop_mailing', 'can stop mailing')], 'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AlterModelOptions(
            name='mailingattempt',
            options={'ordering': ('-latest_attempt',), 'verbose_name': 'Попытка рассылки', 'verbose_name_plural': 'Попытки рассылки'},
        ),
        migrations.AlterModelOptions(
            name='mailingmessage',
            options={'ordering': ('-created_at',), 'verbose_name': 'Сообщение рассылки', 'verbose_name_plural': 'Сообщения рассылкок'},
        ),
    ]