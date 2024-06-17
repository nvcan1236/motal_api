# Generated by Django 5.0.4 on 2024-05-01 15:27

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0010_alter_postimage_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='postforrent',
            name='image',
            field=cloudinary.models.CloudinaryField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='PostImage',
        ),
    ]
