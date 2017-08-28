# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0009_auto_20151027_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='extension',
            field=models.CharField(default='', blank=True, max_length=10, verbose_name='extension'),
            preserve_default=False,
        ),
    ]
