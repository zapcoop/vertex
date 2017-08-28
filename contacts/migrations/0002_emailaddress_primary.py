# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_initial_primary_emails(apps, schema_editor):
    Person = apps.get_model('contacts', 'person')
    User = apps.get_model('auth', 'user')
    EmailAddress = apps.get_model('contacts', 'EmailAddress')

    for person in Person.objects.all():
        if person.user:
            user = person.user
            if user.email:
                try:
                    email = person.email_addresses.get(email_address=user.email)
                except EmailAddress.DoesNotExist:
                    EmailAddress.objects.create(email_address=user.email, person=person)
                else:
                    email.primary = True
                    email.save()
            else:
                email = person.email_addresses.first()
                if email:
                    user.email = email.email_address
                    user.save()


def reverse_data_migration(apps, schema_editor):
    pass  # no-op


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaddress',
            name='primary',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_initial_primary_emails, reverse_code=reverse_data_migration),
    ]
