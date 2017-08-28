from operator import itemgetter
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
import reversion

from contacts.models import GENERIC_INFORMATION_TYPES, PHONE_SPECIFIC_INFORMATION_TYPES
from contacts.rules.organization import is_object_organization_member, is_object_organization_admin
from contacts.rules.person import is_same_organization, is_object_person_manager
from contacts.rules.phonenumber import is_phone_number_owner
from noss import rules
from noss.models import AbstractDatedModel
from noss.rules.predicates import (has_django_permission, is_verified,
                                   is_superuser, is_staff, is_authenticated)


@reversion.register
class PhoneNumber(AbstractDatedModel):
    # PhoneNumber Model
    class Meta:
        unique_together = (('country_code', 'phone_number', 'extension', 'person'),
                           ('country_code', 'phone_number', 'extension', 'organization'))
        verbose_name = _('phone number')
        verbose_name_plural = _('phone numbers')
        app_label = 'contacts'

    country_code = models.CharField(
        _('country code'),
        max_length=10,
        default='1'
    )
    phone_number = models.CharField(
        _('number'),
        max_length=20
    )
    extension = models.CharField(
        _('extension'),
        max_length=10,
        blank=True,
    )
    information_type = models.CharField(
        choices=sorted(
            GENERIC_INFORMATION_TYPES + PHONE_SPECIFIC_INFORMATION_TYPES,
            key=itemgetter(0)
        ),
        max_length=20,
        default='primary'
    )
    person = models.ForeignKey(
        'contacts.Person',
        related_name='phone_numbers',
        verbose_name=_('person'),
        blank=True,
        null=True
    )
    organization = models.ForeignKey(
        'contacts.Organization',
        related_name='phone_numbers',
        verbose_name=_('organization'),
        blank=True,
        null=True
    )

    def clean(self):
        if not self.person and not self.organization:
            raise ValidationError(_('Either a person or an organization must be specified, both cannot be left blank'))

    def save(self, *args, **kwargs):
        # Skip saving if person and organization are blank
        if not self.person and not self.organization:
            return

        if not self.extension:
            self.phone_number, self.extension = self.phone_number_cleaner(self.phone_number)
        else:
            self.phone_number, extra = self.phone_number_cleaner(self.phone_number)

        super().save(*args, **kwargs)

    def __str__(self):
        if self.extension:
            return u"{related_to} {type}: {number} ext.: {extension}".format(
                related_to=self.person if self.person else self.organization,
                type=self.get_information_type_display(),
                number=self.phone_number,
                extension=self.extension
            )
        else:
            return u"{related_to} {type}: {number}".format(
                related_to=self.person if self.person else self.organization,
                type=self.get_information_type_display(),
                number=self.phone_number)

    @classmethod
    def phone_number_cleaner(cls, number):
        phone_number_pattern = re.compile(
            r'''
                        # don't match beginning of string, number can start anywhere
            (\d{3})?    # area code is 3 digits (e.g. '800') and could not be there
            \D*         # optional separator is any number of non-digits
            (\d{3})     # trunk is 3 digits (e.g. '555')
            \D*         # optional separator
            (\d{4})     # rest of number is 4 digits (e.g. '1212')
            \D*         # optional separator
            (\d*)       # extension is optional and can be any number of digits
            \D*         # any trailing chars
            $           # end of string
            ''', re.VERBOSE
        )
        if phone_number_pattern.search(number) is not None:
            result = phone_number_pattern.search(number).groups()
            number = "({areacode}) {trunk}-{number}".format(
                areacode=result[0],
                trunk=result[1],
                number=result[2]
            )
            return number, result[3]
        else:
            return number, ""


rules.add_perm(
    'contacts.view_phonenumber',
    is_superuser & is_verified | is_staff & is_verified |
    is_object_organization_member | is_phone_number_owner | is_same_organization
)
rules.add_perm('contacts.add_phonenumber', is_authenticated)

has_change_or_delete_rights = (
    is_superuser | is_object_organization_admin | is_object_person_manager | is_phone_number_owner
)

rules.add_perm(
    'contacts.change_phonenumber',
    has_change_or_delete_rights | is_staff & has_django_permission('contacts.change_phonenumber')
)
rules.add_perm(
    'contacts.delete_phonenumber',
    has_change_or_delete_rights | is_staff & has_django_permission('contacts.delete_phonenumber')
)
