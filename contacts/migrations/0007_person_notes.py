# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-31 01:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20170831_0052'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
