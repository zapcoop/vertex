# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('service', '0006_rename_note_posted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='tags',
            field=models.ManyToManyField(verbose_name='Tags', to='tags.Tag', blank=True),
        ),
    ]
