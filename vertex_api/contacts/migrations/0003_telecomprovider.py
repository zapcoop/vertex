# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-19 17:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20180104_1901'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelecomProvider',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('contacts.organization',),
        ),
    ]
