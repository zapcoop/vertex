# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0023_orgdepartment_migrate_translated_fields'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='organizationdepartmenttranslation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='organizationdepartmenttranslation',
            name='master',
        ),
        migrations.DeleteModel(
            name='OrganizationDepartmentTranslation',
        ),
    ]
