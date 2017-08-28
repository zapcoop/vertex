# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('contacts', '0012_person_custom_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='tags',
            field=models.ManyToManyField(to='tags.Tag', verbose_name='Tags', related_name='organizations', blank=True),
        ),
    ]
