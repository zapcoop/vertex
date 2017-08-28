# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_auto_20151113_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='update',
            field=models.ForeignKey(to='service.Update', related_name='notes'),
        ),
    ]
