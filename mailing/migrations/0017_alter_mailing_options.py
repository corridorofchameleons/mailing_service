# Generated by Django 5.0.6 on 2024-06-13 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0016_alter_mailing_finish_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailing',
            options={'ordering': ['-created_at', '-start_time'], 'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
    ]
