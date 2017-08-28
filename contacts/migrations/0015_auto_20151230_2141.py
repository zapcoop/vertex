# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0014_auto_20151215_2056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactgrouptranslation',
            old_name='description',
            new_name='description_tmp',
        ),
        migrations.RenameField(
            model_name='contactgrouptranslation',
            old_name='name',
            new_name='name_tmp',
        ),
    ]
