# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-14 17:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20171113_1913'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetstate',
            options={'verbose_name': 'Asset state', 'verbose_name_plural': 'Asset states'},
        ),
        migrations.AlterModelOptions(
            name='state',
            options={'verbose_name': 'State', 'verbose_name_plural': 'States'},
        ),
    ]
