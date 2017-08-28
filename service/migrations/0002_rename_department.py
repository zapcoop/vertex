# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_person_removed'),
        ('django_mailbox', '0004_bytestring_to_unicode'),
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Department',
            new_name='Team'
        ),
        migrations.RenameModel(
            old_name='DepartmentTranslation',
            new_name='TeamTranslation',
        ),
        migrations.AlterField(
            model_name='teamtranslation',
            name='master',
            field=models.ForeignKey(to='service.Team', editable=False, related_name='translations', null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='departments',
            field=models.ManyToManyField(to='service.Team', related_name='tickets'),
        ),
        migrations.AlterModelTable(
            name='teamtranslation',
            table='service_team_translation',
        ),
    ]
