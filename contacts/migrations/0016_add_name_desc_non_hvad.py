# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0015_auto_20151230_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactgroup',
            name='description',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='contactgroup',
            name='name',
            field=models.CharField(max_length=200, verbose_name='name', default='tmp'),
            preserve_default=False,
        ),
    ]
