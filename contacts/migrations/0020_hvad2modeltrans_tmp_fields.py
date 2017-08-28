# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0019_remove_hvad_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organizationdepartmenttranslation',
            old_name='description',
            new_name='description_old',
        ),
        migrations.RenameField(
            model_name='organizationdepartmenttranslation',
            old_name='name',
            new_name='name_old',
        ),
    ]
