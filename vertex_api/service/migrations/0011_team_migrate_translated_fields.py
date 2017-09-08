# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_translated_fields(apps, schema_editor):
    Team = apps.get_model('service', 'Team')
    for team in Team.objects.all():
        for translation in team.translations.all():
            if translation.language_code == 'en':
                team.name_en = translation.name_old
                team.save()
            elif translation.language_code == 'fr':
                team.name_fr = translation.name_old
                team.save()


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0010_team_add_modeltranslation_columns'),
    ]

    operations = [
        migrations.RunPython(migrate_translated_fields),
    ]
