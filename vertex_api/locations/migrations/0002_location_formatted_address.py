# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-04 19:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='formatted_address',
            field=models.CharField(blank=True, editable=False, max_length=200, null=True),
        ),
    ]
