# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_rename_department'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='departments',
            new_name='teams',
        ),
    ]
