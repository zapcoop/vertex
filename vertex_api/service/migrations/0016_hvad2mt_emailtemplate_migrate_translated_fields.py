# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_translated_fields(apps, schema_editor):
    EmailTemplate = apps.get_model('service', 'EmailTemplate')
    for template in EmailTemplate.objects.all():
        for translation in template.translations.all():
            if translation.language_code == 'en':
                template.template_name_en = translation.template_name_old
                template.subject_en = translation.subject
                template.heading_en = translation.heading
                template.plain_text_en = translation.plain_text
                template.markdown_en = translation.markdown
                template.save()
            elif translation.language_code == 'fr':
                template.template_name_fr = translation.template_name_old
                template.subject_fr = translation.subject
                template.heading_fr = translation.heading
                template.plain_text_fr = translation.plain_text
                template.markdown_fr = translation.markdown
                template.save()


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0015_hvad2mt_emailtemplate_translation_columns'),
    ]

    operations = [
        migrations.RunPython(migrate_translated_fields)
    ]
