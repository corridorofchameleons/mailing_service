# Generated by Django 5.0.6 on 2024-05-27 16:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0007_remove_mailing_client_mailing_clients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailing',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mailings', to='mailing.mailingmessage', verbose_name='Сообщение'),
        ),
    ]