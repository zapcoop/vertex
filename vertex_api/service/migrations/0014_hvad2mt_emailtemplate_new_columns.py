# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0013_hvad2mt_emailtemplate_rename_hvad_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='heading',
            field=models.CharField(help_text='In HTML e-mails, this will be the heading at the top of the email - the same context is available as in plain_text, below.', max_length=100, verbose_name='Heading', default='tmp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='markdown',
            field=models.TextField(help_text='The same context is available here as in plain_text, above. The markdown will be rendered as HTML in the e-mail', verbose_name='Markdown', default='tmp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='plain_text',
            field=models.TextField(help_text='The context available to you includes {{ ticket }}, {{ department }}, and depending on the time of the call: {{ resolution }} or {{ comment }}.', verbose_name='Plain Text', default='tmp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='subject',
            field=models.CharField(help_text='This will be prefixed with "[ticket.ticket] ticket.title". We recommend something simple such as "(Updated") or "(Closed)" - the same context is available as in plain_text, below.', max_length=100, verbose_name='Subject', default='tmp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='template_name',
            field=models.CharField(max_length=100, verbose_name='Template Name', default='tmp'),
            preserve_default=False,
        ),
    ]
