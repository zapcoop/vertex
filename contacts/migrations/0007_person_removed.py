# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20151016_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='removed',
            field=models.DateTimeField(null=True, blank=True, editable=False, default=None),
        ),
    ]
