from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
import reversion
from contacts.constants import GENERIC_INFORMATION_TYPES

from contacts.rules.emailaddress import is_email_owner
from contacts.rules.organization import is_object_organization_member, is_object_organization_admin
from contacts.rules.person import is_same_organization, is_object_person_manager
from vertex import rules
from vertex.models import AbstractDatedModel
from vertex.rules import has_django_permission
from vertex.rules.predicates import is_verified, is_superuser, is_staff, is_authenticated


@reversion.register
class EmailAddress(AbstractDatedModel):
    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')
        app_label = 'contacts'

    email_address = models.EmailField(
        _('email address'),
        unique=True
    )
    information_type = models.CharField(
        choices=GENERIC_INFORMATION_TYPES,
        default='primary',
        max_length=20
    )
    person = models.ForeignKey(
        'contacts.Person',
        related_name='email_addresses',
        verbose_name=_('person'),
        blank=True,
        null=True
    )
    organization = models.ForeignKey(
        'contacts.Organization',
        related_name='email_addresses',
        verbose_name=_('organization'),
        blank=True,
        null=True
    )

    primary = models.BooleanField(default=False, editable=False)

    def clean(self):
        if not self.person and not self.organization:
            raise ValidationError(
                _('Either a person or an organization must be specified, both cannot be left blank')
            )

    def __str__(self):
        if self.organization and self.person:
            return "{person} at {organization} <{email}>".format(
                person = self.person.full_name,
                organization= self.organization.name,
                email = self.email_address
            )
        elif self.organization:
            return "{organization} <{email}>".format(
                organization= self.organization,
                email = self.email_address
            )
        elif self.person:
            return "{person} <{email}>".format(
                person=self.person.full_name,
                email=self.email_address
            )
        else:
            return self.email_address

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Skip saving if person and organization are blank
        if not self.person and not self.organization:
            return

        if self.id is None and self.person is not None:
            if not self.person.email_addresses.filter(primary=True).exists():
                self.primary = True
                user = self.person.user
                if user:
                    user.email = self.email_address
                    user.save()
        if self.primary and self.person:
            cache.delete('{app}_{model}_{name}_{id}'.format(
                app=self.person._meta.app_label,
                model=self.person._meta.model_name,
                name='gravatar_url',
                id=self.person.id
            ))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.person and self.person.user and self.email_address == self.person.user.email:
            return
        else:
            super().delete(*args, **kwargs)


rules.add_perm(
    'contacts.view_emailaddress',
    is_superuser & is_verified | is_staff & is_verified |
    is_object_organization_member | is_email_owner |
    is_same_organization
)
rules.add_perm('contacts.add_emailaddress', is_authenticated)

has_change_or_delete_rights = is_superuser | is_object_organization_admin | is_object_person_manager | is_email_owner

rules.add_perm(
    'contacts.change_emailaddress',
    has_change_or_delete_rights | is_staff & has_django_permission('contacts.change_emailaddress')
)
rules.add_perm(
    'contacts.delete_emailaddress',
    has_change_or_delete_rights | is_staff & has_django_permission('contacts.delete_emailaddress')
)
