# Generated by Django 2.0.7 on 2018-07-16 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('external_page', '0022_auto_20180716_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructor',
            name='hobbies',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='external_page.Hobby'),
        ),
    ]
