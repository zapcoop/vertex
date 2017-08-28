# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_auto_20151007_1404'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationAlias',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('organization', models.ForeignKey(to='contacts.Organization', related_name='aliases')),
            ],
        ),
    ]
