# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0020_hvad2modeltrans_tmp_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationdepartment',
            name='description',
            field=models.TextField(blank=True, verbose_name='description', null=True),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='name',
            field=models.CharField(default='tmp', verbose_name='name', max_length=200),
            preserve_default=False,
        ),
    ]
