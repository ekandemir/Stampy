# Generated by Django 3.0 on 2019-12-03 23:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 3, 23, 7, 4, 706450), verbose_name='date_joined'),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2019, 12, 3, 23, 7, 4, 706485), verbose_name='last_login'),
        ),
    ]
