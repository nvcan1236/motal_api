# Generated by Django 5.0.4 on 2024-04-18 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motel', '0008_price_period_alter_motelimage_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='motel',
            name='furniture',
            field=models.CharField(default='Cơ bản', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='motel',
            name='description',
            field=models.CharField(max_length=500),
        ),
        migrations.DeleteModel(
            name='Utility',
        ),
    ]
