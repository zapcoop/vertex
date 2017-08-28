# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0013_organization_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='tags',
            field=models.ManyToManyField(verbose_name='Tags', blank=True, to='tags.Tag'),
        ),
    ]
