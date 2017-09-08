# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0012_team_remove_hvad_columns'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailtemplatetranslation',
            old_name='heading',
            new_name='heading_old',
        ),
        migrations.RenameField(
            model_name='emailtemplatetranslation',
            old_name='markdown',
            new_name='markdown_old',
        ),
        migrations.RenameField(
            model_name='emailtemplatetranslation',
            old_name='plain_text',
            new_name='plain_text_old',
        ),
        migrations.RenameField(
            model_name='emailtemplatetranslation',
            old_name='subject',
            new_name='subject_old',
        ),
        migrations.RenameField(
            model_name='emailtemplatetranslation',
            old_name='template_name',
            new_name='template_name_old',
        ),
    ]
