# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_rename_ticket_departments'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailtemplatetranslation',
            options={'managed': True, 'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='teamtranslation',
            options={'managed': True, 'default_permissions': ()},
        ),
    ]
