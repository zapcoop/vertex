# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0010_auto_20151104_2047'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contactgrouptranslation',
            options={'managed': True, 'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='organizationdepartmenttranslation',
            options={'managed': True, 'default_permissions': ()},
        ),
    ]
