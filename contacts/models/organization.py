from django.db import models
from django.utils.translation import ugettext_lazy as _
import reversion
from uuslug import uuslug

from contacts.rules.organization import is_organization_member
from vertex import rules
from vertex.rules.predicates import has_django_permission, is_staff, is_superuser
from vertex.models import AbstractDatedModel

__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


@reversion.register
class Organization(AbstractDatedModel):
    """Organization model."""
    slug = models.SlugField(editable=False)

    parent = models.ForeignKey(
        'self',
        verbose_name=_("Parent"),
        blank=True,
        null=True,
        related_name='children'
    )

    name = models.CharField(
        _('Name'),
        max_length=200
    )

    people = models.ManyToManyField(
        "contacts.Person",
        related_name='organizations',

    )

    administrators = models.ManyToManyField(
        "contacts.Person",
        related_name='managed_organizations',
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        app_label = 'contacts'

    def __str__(self):
        return u"{name}".format(name=self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuslug(self.full_name, instance=self)

        super(Organization, self).save(*args, **kwargs)


class OrganizationAlias(AbstractDatedModel):
    name = models.CharField(max_length=200)
    organization = models.ForeignKey('contacts.Organization', related_name='aliases')

    class Meta:
        ordering = ('name',)
        verbose_name = _('organization alias')
        verbose_name_plural = _('organization aliases')
        app_label = 'contacts'

    def __str__(self):
        return '{} alias of {}'.format(self.name, self.organization.name)


rules.add_perm('contacts.view_organization', is_superuser | is_staff | is_organization_member)
rules.add_perm('contacts.add_organization',
               is_superuser | is_staff & has_django_permission('contacts.add_organization'))
rules.add_perm('contacts.change_organization',
               is_superuser | is_staff & has_django_permission('contacts.change_organization'))
rules.add_perm('contacts.delete_organization',
               is_superuser | is_staff & has_django_permission('contacts.delete_organization'))
