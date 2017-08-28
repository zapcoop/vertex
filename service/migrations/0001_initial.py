# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0004_bytestring_to_unicode'),
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('slug', models.SlugField(verbose_name='Slug', help_text="This slug is used when building ticket ID's. Once set, try not to change it or e-mailing may get messy.")),
                ('email_address', models.EmailField(null=True, verbose_name='E-Mail Address', max_length=254, blank=True, help_text='All outgoing e-mails for this department will use this e-mail address. If you use IMAP or POP3, this should be the e-mail address for that mailbox.')),
                ('allow_email_submission', models.BooleanField(verbose_name='Allow E-Mail Submission?', default=False, help_text='Do you want to poll the e-mail box below for new tickets?')),
                ('escalate_after', models.IntegerField(null=True, verbose_name='Escalation minutes', blank=True, help_text='For tickets which are not held, how often do you wish to increase their priority? Set to 0 for no escalation.')),
                ('allowed_organization_departments', models.ManyToManyField(to='contacts.OrganizationDepartment', related_name='service_departments', help_text='The selected organization department people with staff status will be allowed to view and interact with all the tickets in this service department.')),
                ('mailbox', models.OneToOneField(to='django_mailbox.Mailbox')),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'ordering': ('slug',),
            },
        ),
        migrations.CreateModel(
            name='DepartmentTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', null=True, to='service.Department', editable=False)),
            ],
            options={
                'db_tablespace': '',
                'abstract': False,
                'db_table': 'service_department_translation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'e-mail template',
                'verbose_name_plural': 'e-mail templates',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplateTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_name', models.CharField(verbose_name='Template Name', max_length=100)),
                ('subject', models.CharField(verbose_name='Subject', max_length=100, help_text='This will be prefixed with "[ticket.ticket] ticket.title". We recommend something simple such as "(Updated") or "(Closed)" - the same context is available as in plain_text, below.')),
                ('heading', models.CharField(verbose_name='Heading', max_length=100, help_text='In HTML e-mails, this will be the heading at the top of the email - the same context is available as in plain_text, below.')),
                ('plain_text', models.TextField(verbose_name='Plain Text', help_text='The context available to you includes {{ ticket }}, {{ department }}, and depending on the time of the call: {{ resolution }} or {{ comment }}.')),
                ('markdown', models.TextField(verbose_name='Markdown', help_text='The same context is available here as in plain_text, above. The markdown will be rendered as HTML in the e-mail')),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', null=True, to='service.EmailTemplate', editable=False)),
            ],
            options={
                'db_tablespace': '',
                'abstract': False,
                'db_table': 'service_emailtemplate_translation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('body', models.TextField(verbose_name='Body')),
                ('posted_by', models.ForeignKey(to='contacts.Person', editable=False)),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('title', models.CharField(verbose_name='Title', max_length=200)),
                ('status', django_fsm.FSMIntegerField(protected=True, verbose_name='Status', choices=[(0, 'New'), (1, 'In progress'), (2, 'Waiting for customer'), (3, 'On hold'), (4, 'Resolved'), (5, 'Follow-up sent'), (6, 'Re-opened'), (7, 'Closed'), (8, 'Duplicate')], default=0, editable=False)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True, help_text='The content of the query.')),
                ('description_is_plain', models.BooleanField(default=False)),
                ('resolution', models.TextField(null=True, verbose_name='Resolution', blank=True, help_text='The resolution provided by our staff.')),
                ('priority', models.IntegerField(verbose_name='Priority', choices=[(1, 'P1. Critical'), (2, 'P2. High'), (3, 'P3. Normal'), (4, 'P4. Low'), (5, 'P5. Very Low')], help_text='1 = Highest Priority, 5 = Low Priority')),
                ('signaled_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('due_date', models.DateTimeField(null=True, verbose_name='Due on', blank=True)),
                ('last_escalation', models.DateTimeField(null=True, editable=False, blank=True, help_text='The date this ticket was last escalated - updated automatically')),
                ('message_id', models.CharField(editable=False, max_length=255, default='')),
                ('assigned_to', models.ForeignKey(verbose_name='Assigned to', related_name='assigned_tickets', blank=True, null=True, to='contacts.Person')),
                ('created_by', models.ForeignKey(verbose_name='Created by', related_name='created_tickets', blank=True, null=True, to='contacts.Person')),
                ('departments', models.ManyToManyField(to='service.Department', related_name='tickets')),
                ('duplicate_of', models.ForeignKey(related_name='duplicates', null=True, to='service.Ticket', editable=False)),
                ('organization', models.ForeignKey(null=True, to='contacts.Organization')),
                ('parent', models.ForeignKey(related_name='children', null=True, to='service.Ticket', editable=False)),
                ('signaled_by', models.ForeignKey(verbose_name='Signaled by', related_name='originated_tickets', blank=True, null=True, to='contacts.Person')),
            ],
            options={
                'get_latest_by': 'created_at',
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='TicketChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(verbose_name='Field', max_length=100)),
                ('old_value', models.TextField(null=True, verbose_name='Old Value', blank=True)),
                ('new_value', models.TextField(null=True, verbose_name='New Value', blank=True)),
            ],
            options={
                'verbose_name': 'Ticket change',
                'verbose_name_plural': 'Ticket changes',
            },
        ),
        migrations.CreateModel(
            name='TicketCommunication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.OneToOneField(to='django_mailbox.Message')),
                ('ticket', models.ForeignKey(to='service.Ticket')),
            ],
        ),
        migrations.CreateModel(
            name='TicketSubscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('can_view', models.BooleanField(verbose_name='Can View Ticket?', default=False, help_text='Can this person view the ticket details?')),
                ('can_update', models.BooleanField(verbose_name='Can Update Ticket?', default=False, help_text='Can this person change/update the ticket?')),
                ('email_address', models.ForeignKey(verbose_name='Email address', related_name='ticket_subscriptions', to='contacts.EmailAddress', help_text='Where to send updates for this ticket?')),
                ('ticket', models.ForeignKey(verbose_name='Ticket', related_name='subscribers', to='service.Ticket')),
            ],
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(null=True, verbose_name='modified at', auto_now=True)),
                ('display_time', models.DateTimeField(verbose_name='Date', default=django.utils.timezone.now)),
                ('body', models.TextField(verbose_name='Body', blank=True)),
                ('body_is_plaintext', models.BooleanField(default=False)),
                ('duration', models.DurationField(null=True, verbose_name='Duration', blank=True)),
                ('billable_hours', models.DurationField(null=True, verbose_name='Billable hours', blank=True)),
                ('message_id', models.CharField(editable=False, max_length=255, blank=True)),
                ('email_address', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='contacts.EmailAddress', editable=False)),
                ('person', models.ForeignKey(verbose_name='Person', null=True, to='contacts.Person', editable=False)),
                ('ticket', models.ForeignKey(verbose_name='Ticket', related_name='updates', to='service.Ticket', editable=False)),
            ],
            options={
                'verbose_name': 'Update',
                'verbose_name_plural': 'Updates',
                'ordering': ['display_time'],
            },
        ),
        migrations.AddField(
            model_name='ticketchange',
            name='update',
            field=models.ForeignKey(to='service.Update'),
        ),
        migrations.AddField(
            model_name='note',
            name='update',
            field=models.ForeignKey(to='service.Update'),
        ),
        migrations.AlterUniqueTogether(
            name='emailtemplatetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='departmenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
