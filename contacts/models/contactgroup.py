from django.db import models
from django.utils.translation import ugettext_lazy as _
import reversion

from vertex.models import AbstractDatedModel

__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


@reversion.register
class ContactGroup(AbstractDatedModel):
    """ContactGroup model."""

    name = models.CharField(
        _('name'),
        max_length=200,
    )
    description = models.TextField(
        _('description'),
        blank=True,
        null=True
    )

    people = models.ManyToManyField(
        'contacts.Person',
        verbose_name=_('people'),
        blank=True,
        related_name='groups'
    )
    organizations = models.ManyToManyField(
        'contacts.Organization',
        verbose_name=_('organization'),
        blank=True,
        related_name='groups'
    )

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        app_label = 'contacts'

    def __str__(self):
        return u"%s" % self.name

    def delete(self, *args, **kwargs):
        if self.id <= 5:
            return
        else:
            super().delete(*args, **kwargs)  # Call the "real" delete() method.
