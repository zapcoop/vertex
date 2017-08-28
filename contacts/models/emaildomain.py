from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import reversion

from noss.models import AbstractDatedModel
from noss.utils.softdeletion import SoftDeletableModel
from . import EmailAddress

__author__ = 'jsenecal'


@reversion.register
class EmailDomain(SoftDeletableModel, AbstractDatedModel):
    """EmailDomain model."""

    organization = models.ForeignKey(
        'contacts.Organization',
        verbose_name=_('organization'),
        related_name='email_domains'
    )

    domain_name = models.CharField(
        _('domain name'),
        max_length=200,
        validators=[RegexValidator('^[a-z0-9]+\.[a-z0-9]{1,4}$')],
        unique=True
    )

    class Meta:
        ordering = ('domain_name',)
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        app_label = 'contacts'

    def __str__(self):
        return u"%s" % self.domain_name


@receiver(signal=post_save, sender=EmailDomain)
def sync_people_email_addresses(instance, **kwargs):

    domain_part = "@{:}".format(instance.domain_name)
    EmailAddress.objects.filter(email_address__icontains=domain_part, person__isnull=False).update(organization=instance.organization)