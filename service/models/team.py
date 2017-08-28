from django.conf import settings
from django.db import models

from noss.models import AbstractDatedModel
from noss import rules
from noss.rules.predicates import has_django_permission, is_staff, is_superuser
from ..rules.department import is_team_member


__author__ = 'jsenecal'
from django.utils.translation import ugettext_lazy as _


class Team(AbstractDatedModel):
    """
    A department is a collection of tickets into what would generally be business
    areas or departments.
    For example, a company may have a department for each Product they provide, or
    a department for each of Accounts, Pre-Sales, and Support.
    """

    name = models.CharField(
        _('Name'),
        max_length=100
    )

    slug = models.SlugField(
        _('Slug'),
        help_text=_('This slug is used when building ticket ID\'s. Once set, '
                    'try not to change it or e-mailing may get messy.'),
    )

    allowed_organization_departments = models.ManyToManyField(
        'contacts.OrganizationDepartment',
        help_text=_('The selected organization department people with staff status '
                    'will be allowed to view and interact with all the tickets in this service department.'),
        related_name='service_departments'
    )

    email_address = models.EmailField(
        _('E-Mail Address'),
        blank=True,
        null=True,
        help_text=_('All outgoing e-mails for this department will use this e-mail '
                    'address. If you use IMAP or POP3, this should be the e-mail '
                    'address for that mailbox.'),
    )

    mailbox = models.OneToOneField(
        'django_mailbox.Mailbox'
    )

    allow_email_submission = models.BooleanField(
        _('Allow E-Mail Submission?'),
        blank=True,
        default=False,
        help_text=_('Do you want to poll the e-mail box below for new '
                    'tickets?'),
    )

    escalate_after = models.IntegerField(
        _('Escalation minutes'),
        blank=True,
        null=True,
        help_text=_('For tickets which are not held, how often do you wish to '
                    'increase their priority? Set to 0 for no escalation.'),
    )

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ('slug',)
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        app_label = "service"

    @property
    def smtp_from_address(self):
        """
        Short property to provide a sender address in SMTP format,
        eg 'Name <email>'. We do this so we can put a simple error message
        in the sender name field, so hopefully the admin can see and fix it.
        """
        if not self.email_address:
            return u'NO DEPARTMENT EMAIL ADDRESS DEFINED <%s>' % settings.DEFAULT_FROM_EMAIL
        else:
            return u'%s <%s>' % (self.name, self.email_address)


rules.add_perm('service.view_department', is_superuser | is_staff | is_team_member)
rules.add_perm('service.add_department', is_superuser | is_staff & has_django_permission('service.add_department'))
rules.add_perm('service.change_department', is_superuser | is_staff & has_django_permission('service.change_department'))
rules.add_perm('service.delete_department', is_superuser | is_staff & has_django_permission('service.delete_department'))
