# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0021_hvad2modeltrans_new_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationdepartment',
            name='description_en',
            field=models.TextField(verbose_name='description', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='description_fr',
            field=models.TextField(verbose_name='description', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='name_en',
            field=models.CharField(max_length=200, verbose_name='name', null=True),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='name_fr',
            field=models.CharField(max_length=200, verbose_name='name', null=True),
        ),
    ]
