# Generated by Django 5.0.6 on 2024-05-27 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0004_remove_client_mailing_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailing',
            name='message',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='mailing', to='mailing.mailingmessage', verbose_name='Сообщение'),
        ),
    ]
