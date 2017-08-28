# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20151016_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='active',
        ),
        migrations.AddField(
            model_name='emaildomain',
            name='removed',
            field=models.DateTimeField(editable=False, blank=True, null=True, default=None),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='removed',
            field=models.DateTimeField(editable=False, blank=True, null=True, default=None),
        ),
    ]
