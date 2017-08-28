# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import noss.fields
from django.conf import settings
import django.core.validators
import noss.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='ContactGroupTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=200)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', null=True, to='contacts.ContactGroup', editable=False)),
            ],
            options={
                'db_tablespace': '',
                'abstract': False,
                'db_table': 'contacts_contactgroup_translation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('email_address', models.EmailField(verbose_name='email address', max_length=254, unique=True)),
                ('information_type', models.CharField(choices=[('assistant', 'Assistant'), ('business', 'Business'), ('business-other', 'Business, other'), ('company', 'Company'), ('home', 'Home'), ('home-other', 'Home, other'), ('other', 'Other'), ('primary', 'Primary')], max_length=20, default='primary')),
            ],
            options={
                'verbose_name': 'email address',
                'verbose_name_plural': 'email addresses',
            },
        ),
        migrations.CreateModel(
            name='EmailDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('domain_name', models.CharField(verbose_name='domain name', max_length=200, validators=[django.core.validators.RegexValidator('^[a-z0-9]+\\.[a-z0-9]{1,4}$')], unique=True)),
            ],
            options={
                'verbose_name': 'department',
                'verbose_name_plural': 'departments',
                'ordering': ('domain_name',),
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('nickname', models.CharField(null=True, verbose_name='Nickname', max_length=50, blank=True)),
                ('reference', noss.fields.AutoReferenceField(verbose_name='Reference', sep='', slugify=noss.utils.slugify_spaceless, editable=False, populate_from='name', unique=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('disabled', models.BooleanField(verbose_name='disabled', editable=False, default=False)),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='OrganizationDepartment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
            ],
            options={
                'verbose_name': 'department',
                'verbose_name_plural': 'departments',
            },
        ),
        migrations.CreateModel(
            name='OrganizationDepartmentTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=200)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', null=True, to='contacts.OrganizationDepartment', editable=False)),
            ],
            options={
                'db_tablespace': '',
                'abstract': False,
                'db_table': 'contacts_organizationdepartment_translation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('title', models.CharField(null=True, verbose_name='Title', max_length=20, blank=True)),
                ('first_name', models.CharField(verbose_name='First name', max_length=100)),
                ('middle_name', models.CharField(null=True, verbose_name='Middle name', max_length=100, blank=True)),
                ('last_name', models.CharField(verbose_name='Last name', max_length=100)),
                ('suffix', models.CharField(null=True, verbose_name='Suffix', max_length=20, blank=True)),
                ('nickname', models.CharField(null=True, verbose_name='Nickname', max_length=20, blank=True)),
                ('active', models.BooleanField(editable=False, default=True)),
                ('user', models.OneToOneField(blank=True, null=True, to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'People',
                'ordering': ('last_name', 'first_name'),
                'permissions': (('view_person', 'Can view person'),),
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('country_code', models.CharField(verbose_name='country code', max_length=10, default='1')),
                ('phone_number', models.CharField(verbose_name='number', max_length=20)),
                ('extension', models.CharField(null=True, verbose_name='extension', max_length=10, blank=True)),
                ('information_type', models.CharField(choices=[('assistant', 'Assistant'), ('business', 'Business'), ('business-fax', 'Business fax'), ('business-other', 'Business, other'), ('callback', 'Callback'), ('car', 'Car'), ('company', 'Company'), ('home', 'Home'), ('home-fax', 'Home fax'), ('home-other', 'Home, other'), ('isdn', 'ISDN'), ('mobile', 'Mobile'), ('other', 'Other'), ('other-fax', 'Other fax'), ('pager', 'Pager'), ('primary', 'Primary'), ('radio', 'Radio'), ('tty-tdd', 'TTY/TDD')], max_length=20, default='primary')),
                ('organization', models.ForeignKey(verbose_name='organization', related_name='phone_numbers', blank=True, null=True, to='contacts.Organization')),
                ('person', models.ForeignKey(verbose_name='person', related_name='phone_numbers', blank=True, null=True, to='contacts.Person')),
            ],
            options={
                'verbose_name': 'phone number',
                'verbose_name_plural': 'phone numbers',
            },
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('url', models.URLField(verbose_name='URL')),
                ('information_type', models.CharField(choices=[('Social media', (('apple', 'Apple'), ('behance', 'Behance'), ('bitbucket', 'BitBucket'), ('delicious', 'Delicious'), ('deviantart', 'DeviantArt'), ('facebook', 'Facebook'), ('flickr', 'Flickr'), ('github', 'Github'), ('googleplus', 'Google+'), ('instagram', 'Instagram'), ('linkedin', 'LinkedIn'), ('pinterest', 'Pinterest'), ('reddit', 'Reddit'), ('tumblr', 'Tumblr'), ('twitter', 'Twitter'), ('youtube', 'YouTube'))), ('Web site', (('assistant', 'Assistant'), ('business', 'Business'), ('business-other', 'Business, other'), ('company', 'Company'), ('home', 'Home'), ('home-other', 'Home, other'), ('other', 'Other'), ('primary', 'Primary')))], max_length=12)),
                ('organization', models.ForeignKey(verbose_name='organization', related_name='urls', blank=True, null=True, to='contacts.Organization')),
                ('person', models.ForeignKey(verbose_name='person', related_name='urls', blank=True, null=True, to='contacts.Person')),
            ],
            options={
                'verbose_name': 'URL',
                'verbose_name_plural': 'URLs',
            },
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='managers',
            field=models.ManyToManyField(verbose_name='managers', to='contacts.Person', related_name='managed_departments', blank=True),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='organization',
            field=models.ForeignKey(verbose_name='organization', related_name='departments', to='contacts.Organization'),
        ),
        migrations.AddField(
            model_name='organizationdepartment',
            name='people',
            field=models.ManyToManyField(verbose_name='people', to='contacts.Person', related_name='departments', blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='administrators',
            field=models.ManyToManyField(to='contacts.Person', related_name='managed_organizations'),
        ),
        migrations.AddField(
            model_name='organization',
            name='customers',
            field=models.ManyToManyField(verbose_name='Customers', to='contacts.Organization', related_name='resellers', blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='parent',
            field=models.ForeignKey(verbose_name='Parent', related_name='children', blank=True, null=True, to='contacts.Organization'),
        ),
        migrations.AddField(
            model_name='organization',
            name='people',
            field=models.ManyToManyField(to='contacts.Person', related_name='organizations'),
        ),
        migrations.AddField(
            model_name='emaildomain',
            name='organization',
            field=models.ForeignKey(verbose_name='organization', related_name='email_domains', to='contacts.Organization'),
        ),
        migrations.AddField(
            model_name='emailaddress',
            name='organization',
            field=models.ForeignKey(verbose_name='organization', related_name='email_addresses', blank=True, null=True, to='contacts.Organization'),
        ),
        migrations.AddField(
            model_name='emailaddress',
            name='person',
            field=models.ForeignKey(verbose_name='person', related_name='email_addresses', blank=True, null=True, to='contacts.Person'),
        ),
        migrations.AddField(
            model_name='contactgroup',
            name='organizations',
            field=models.ManyToManyField(verbose_name='organization', to='contacts.Organization', related_name='groups', blank=True),
        ),
        migrations.AddField(
            model_name='contactgroup',
            name='people',
            field=models.ManyToManyField(verbose_name='people', to='contacts.Person', related_name='groups', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='phonenumber',
            unique_together=set([('country_code', 'phone_number', 'extension', 'person'), ('country_code', 'phone_number', 'extension', 'organization')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationdepartmenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='contactgrouptranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
