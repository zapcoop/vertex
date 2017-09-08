# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_change_note_update_related_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='note',
            old_name='posted_by',
            new_name='person',
        ),
    ]
