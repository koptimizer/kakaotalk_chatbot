# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-14 22:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20171014_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='shuttle',
            name='Time_Start',
            field=models.TimeField(default=None, null=True),
        ),
    ]