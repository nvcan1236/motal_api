# Generated by Django 5.0.4 on 2024-04-18 03:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motel', '0006_rename_dientich_motel_area_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='motelimage',
            old_name='source',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='motelimage',
            name='motel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='motel_images', to='motel.motel'),
        ),
    ]