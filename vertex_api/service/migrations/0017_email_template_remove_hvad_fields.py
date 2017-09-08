# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0016_hvad2mt_emailtemplate_migrate_translated_fields'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='emailtemplatetranslation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='emailtemplatetranslation',
            name='master',
        ),
        migrations.DeleteModel(
            name='EmailTemplateTranslation',
        ),
    ]
