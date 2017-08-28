from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
import reversion

from contacts.models import URL_SPECIFIC_INFORMATION_TYPES
from contacts.rules.organization import is_object_organization_admin, is_object_organization_member
from contacts.rules.person import is_same_organization, is_object_person_manager
from contacts.rules.url import is_url_owner
from noss import rules
from noss.models import AbstractDatedModel
from noss.rules import has_django_permission
from noss.rules.predicates import is_verified, is_superuser, is_staff, is_authenticated


@reversion.register
class URL(AbstractDatedModel):
    class Meta:
        verbose_name = _('URL')
        verbose_name_plural = _('URLs')
        app_label = 'contacts'

    url = models.URLField(
        _('URL')
    )
    information_type = models.CharField(
        choices=URL_SPECIFIC_INFORMATION_TYPES,
        max_length=12
    )
    person = models.ForeignKey(
        'contacts.Person',
        related_name='urls',
        verbose_name=_('person'),
        blank=True,
        null=True
    )
    organization = models.ForeignKey(
        'contacts.Organization',
        related_name='urls',
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
        super(URL, self).save(*args, **kwargs)


rules.add_perm(
    'contacts.view_url',
    is_superuser & is_verified | is_staff & is_verified |
    is_object_organization_member | is_url_owner | is_same_organization
)
rules.add_perm('contacts.add_url', is_authenticated)

has_change_or_delete_rights = is_superuser | is_object_organization_admin | is_object_person_manager | is_url_owner

rules.add_perm(
    'contacts.change_url',
    has_change_or_delete_rights | is_staff & has_django_permission('contacts.change_url')
)
rules.add_perm(
    'contacts.delete_url',
    has_change_or_delete_rights | is_staff & has_django_permission('contacts.delete_url')
)
