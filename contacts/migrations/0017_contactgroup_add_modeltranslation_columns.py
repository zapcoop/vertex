# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0016_add_name_desc_non_hvad'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactgroup',
            name='description_en',
            field=models.TextField(verbose_name='description', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='contactgroup',
            name='description_fr',
            field=models.TextField(verbose_name='description', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='contactgroup',
            name='name_en',
            field=models.CharField(verbose_name='name', null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='contactgroup',
            name='name_fr',
            field=models.CharField(verbose_name='name', null=True, max_length=200),
        ),
    ]
