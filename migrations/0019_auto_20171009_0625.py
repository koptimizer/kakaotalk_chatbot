# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-09 06:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20171009_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='message',
            field=models.TextField(default=None, null=True),
        ),
    ]