# Generated by Django 5.0.4 on 2024-05-01 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motel', '0014_motel_approved_alter_reservation_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='expiration',
            field=models.DateTimeField(default='2024-05-04 14:43:16'),
        ),
    ]
