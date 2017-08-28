# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_auto_20151022_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date of birth', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=5),
        ),
    ]
