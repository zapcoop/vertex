# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0007_ticket_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teamtranslation',
            old_name='name',
            new_name='name_old',
        ),
    ]
