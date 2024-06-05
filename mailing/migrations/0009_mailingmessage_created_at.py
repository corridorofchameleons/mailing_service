# Generated by Django 5.0.6 on 2024-06-05 16:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0008_alter_mailing_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailingmessage',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
    ]
