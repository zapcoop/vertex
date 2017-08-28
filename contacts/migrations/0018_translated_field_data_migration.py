# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_translated_fields(apps, schema_editor):
    ContactGroup = apps.get_model('contacts', 'ContactGroup')
    for contact_group in ContactGroup.objects.all():
        for translation in contact_group.translations.all():
            if translation.language_code == 'en':
                contact_group.name_en = translation.name_tmp
                contact_group.description_en = translation.description_tmp
                contact_group.save()
            elif translation.language_code == 'fr':
                contact_group.name_fr = translation.name_tmp
                contact_group.description_fr = translation.description_tmp
                contact_group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0017_contactgroup_add_modeltranslation_columns'),
    ]

    operations = [
        migrations.RunPython(migrate_translated_fields),
    ]
