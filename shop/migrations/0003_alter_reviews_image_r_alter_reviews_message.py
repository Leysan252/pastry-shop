# Generated by Django 4.0.4 on 2022-07-13 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_reviews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='image_r',
            field=models.ImageField(blank=True, upload_to='reviews/'),
        ),
        migrations.AlterField(
            model_name='reviews',
            name='message',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
