# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-28 16:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0009_manufacturer'),
    ]

    operations = [
        migrations.CreateModel(
            name='HardwareSupplier',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('contacts.organization',),
        ),
    ]
