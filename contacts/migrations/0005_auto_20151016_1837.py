# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_organizationalias'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='disabled',
        ),
        migrations.AddField(
            model_name='organization',
            name='removed',
            field=models.DateTimeField(null=True, default=None, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='organizationalias',
            name='removed',
            field=models.DateTimeField(null=True, default=None, blank=True, editable=False),
        ),
    ]
