from django.db import models
from django.utils.translation import ugettext_lazy as _
import reversion

from contacts.rules.department import is_department_member, is_department_manager
from contacts.rules.organization import is_object_organization_admin
from vertex import rules
from vertex.models import AbstractDatedModel
from vertex.rules.predicates import has_django_permission, is_superuser, is_staff
from vertex.utils.softdeletion import SoftDeletableModel


@reversion.register
class OrganizationDepartment(AbstractDatedModel, SoftDeletableModel):
    """OrganizationDepartment model."""

    organization = models.ForeignKey(
        'contacts.Organization',
        verbose_name=_('organization'),
        related_name='departments'
    )

    name = models.CharField(
        _('name'),
        max_length=200
    )

    description = models.TextField(
        _('description'),
        blank=True,
        null=True
    )

    people = models.ManyToManyField(
        'contacts.Person',
        verbose_name=_('people'),
        related_name='departments',
        blank=True
    )
    managers = models.ManyToManyField(
        'contacts.Person',
        verbose_name=_('managers'),
        related_name='managed_departments',
        blank=True
    )

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        app_label = 'contacts'

    def __str__(self):
        return u"%s" % self.name


rules.add_perm(
    'contacts.view_department',
    is_superuser | is_staff | is_department_member | is_object_organization_admin
)
rules.add_perm(
    'contacts.add_department',
    is_superuser | is_object_organization_admin |
    is_staff & has_django_permission(
        'contacts.add_department'
    )
)
rules.add_perm(
    'contacts.change_department',
    is_superuser | is_object_organization_admin | is_department_manager |
    is_staff & has_django_permission(
        'contacts.change_department'
    )
)
rules.add_perm(
    'contacts.delete_department',
    is_superuser | is_object_organization_admin |
    is_staff & has_django_permission(
        'contacts.delete_department'
    )
)