# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_translated_fields(apps, schema_editor):
    OrganizationDepartment = apps.get_model('contacts', 'OrganizationDepartment')
    for department in OrganizationDepartment.objects.all():
        for translation in department.translations.all():
            if translation.language_code == 'en':
                department.name_en = translation.name_old
                department.description_en = translation.description_old
                department.save()
            elif translation.language_code == 'fr':
                department.name_fr = translation.name_old
                department.description_fr = translation.description_old
                department.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0022_orgdepartment_add_translation_columns'),
    ]

    operations = [
        migrations.RunPython(migrate_translated_fields),
    ]
