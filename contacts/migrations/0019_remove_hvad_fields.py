# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0018_translated_field_data_migration'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contactgrouptranslation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='contactgrouptranslation',
            name='master',
        ),
        migrations.DeleteModel(
            name='ContactGroupTranslation',
        ),
    ]
