# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0008_team_rename_hvad_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name', default='tmp'),
            preserve_default=False,
        ),
    ]
