# Generated by Django 5.0.4 on 2024-05-03 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motel', '0017_alter_motelimage_motel_alter_reservation_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='expiration',
            field=models.DateTimeField(default='2024-05-06 10:43:59'),
        ),
    ]
