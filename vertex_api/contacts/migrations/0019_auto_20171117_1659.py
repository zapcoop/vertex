# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-17 16:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0018_auto_20171117_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='organizations', to='contacts.ContactGroup', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='peopleorganizations',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='people', to='contacts.ContactGroup', verbose_name='groups'),
        ),
    ]
