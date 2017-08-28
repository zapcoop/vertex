# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0011_auto_20151113_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='custom_avatar_url',
            field=models.URLField(blank=True),
        ),
    ]
