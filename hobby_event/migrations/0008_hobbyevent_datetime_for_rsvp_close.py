# Generated by Django 2.0.7 on 2018-07-21 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hobby_event', '0007_auto_20180721_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='hobbyevent',
            name='datetime_for_rsvp_close',
            field=models.DateTimeField(null=True),
        ),
    ]
