# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0011_team_migrate_translated_fields'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='teamtranslation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='teamtranslation',
            name='master',
        ),
        migrations.DeleteModel(
            name='TeamTranslation',
        ),
    ]
