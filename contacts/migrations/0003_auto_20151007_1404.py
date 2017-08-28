# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_emailaddress_primary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='primary',
            field=models.BooleanField(editable=False, default=False),
        ),
    ]
