# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import noss.utils
import noss.fields


class Migration(migrations.Migration):
    dependencies = [
        ('contacts', '0007_person_removed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='reference',
            field=noss.fields.AutoReferenceField(slugify=noss.utils.slugify_spaceless, verbose_name='Reference', sep='',
                                                 max_length=6, populate_from='name', unique=True, editable=False),
        ),
    ]
