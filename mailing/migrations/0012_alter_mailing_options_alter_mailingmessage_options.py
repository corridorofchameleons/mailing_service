# Generated by Django 5.0.6 on 2024-06-05 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0011_mailing_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailing',
            options={'ordering': ['-created_at'], 'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AlterModelOptions(
            name='mailingmessage',
            options={'ordering': ['-created_at'], 'verbose_name': 'Сообщение рассылки', 'verbose_name_plural': 'Сообщения рассылкок'},
        ),
    ]