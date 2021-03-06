# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-04 18:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('places', '0003_auto_20171130_1855'),
    ]

    operations = [
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('label', models.CharField(help_text='Enter the label for this floor just as it would appear in an elevator or on fire escape plans.', max_length=30, verbose_name='Floor label')),
                ('number', models.IntegerField(help_text='Enter the floor number relative to ground level. Ground level equals 0.', verbose_name='Number')),
                ('elevation', models.FloatField(blank=True, help_text='Enter the elevation in meters above sea level.', null=True)),
            ],
            options={
                'verbose_name': 'Floor',
                'verbose_name_plural': 'Floors',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('raw_address', models.CharField(blank=True, max_length=200, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('place', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='places.Place')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('label', models.CharField(help_text='Enter the label for this room just as it is found in that location or create one using alphanumeric characters.', max_length=30, verbose_name='Floor label')),
                ('notes', models.TextField(blank=True, null=True)),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.Floor')),
                ('place', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='places.Place')),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
                'ordering': ['floor'],
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('site_tag', models.SlugField(editable=False, max_length=8, unique=True, verbose_name='Site tag')),
                ('facility', models.CharField(blank=True, help_text='Used to include an external designation such as a data center name (e.g. Equinix TR1)', max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('places', models.ManyToManyField(to='places.Place')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='floor',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.Location'),
        ),
        migrations.AddField(
            model_name='floor',
            name='place',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='places.Place'),
        ),
    ]
