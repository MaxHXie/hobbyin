# Generated by Django 2.0.7 on 2018-07-21 17:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hobby_event', '0010_auto_20180721_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='hobbyevent',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
