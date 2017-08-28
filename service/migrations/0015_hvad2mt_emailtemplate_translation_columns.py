# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0014_hvad2mt_emailtemplate_new_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='heading_en',
            field=models.CharField(verbose_name='Heading', help_text='In HTML e-mails, this will be the heading at the top of the email - the same context is available as in plain_text, below.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='heading_fr',
            field=models.CharField(verbose_name='Heading', help_text='In HTML e-mails, this will be the heading at the top of the email - the same context is available as in plain_text, below.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='markdown_en',
            field=models.TextField(verbose_name='Markdown', help_text='The same context is available here as in plain_text, above. The markdown will be rendered as HTML in the e-mail', null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='markdown_fr',
            field=models.TextField(verbose_name='Markdown', help_text='The same context is available here as in plain_text, above. The markdown will be rendered as HTML in the e-mail', null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='plain_text_en',
            field=models.TextField(verbose_name='Plain Text', help_text='The context available to you includes {{ ticket }}, {{ department }}, and depending on the time of the call: {{ resolution }} or {{ comment }}.', null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='plain_text_fr',
            field=models.TextField(verbose_name='Plain Text', help_text='The context available to you includes {{ ticket }}, {{ department }}, and depending on the time of the call: {{ resolution }} or {{ comment }}.', null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='subject_en',
            field=models.CharField(verbose_name='Subject', help_text='This will be prefixed with "[ticket.ticket] ticket.title". We recommend something simple such as "(Updated") or "(Closed)" - the same context is available as in plain_text, below.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='subject_fr',
            field=models.CharField(verbose_name='Subject', help_text='This will be prefixed with "[ticket.ticket] ticket.title". We recommend something simple such as "(Updated") or "(Closed)" - the same context is available as in plain_text, below.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='template_name_en',
            field=models.CharField(verbose_name='Template Name', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='template_name_fr',
            field=models.CharField(verbose_name='Template Name', max_length=100, null=True),
        ),
    ]
