# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0009_add_name_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='name_en',
            field=models.CharField(verbose_name='Name', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='name_fr',
            field=models.CharField(verbose_name='Name', max_length=100, null=True),
        ),
    ]
