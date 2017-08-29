from django.db import models
from django.utils.translation import ugettext_lazy as _

from vertex.models import AbstractDatedModel


__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


class BlacklistedEmail(AbstractDatedModel, models.Model):
    """
    This model lets us easily ignore e-mails from certain senders when
    processing IMAP and POP3 mailboxes, eg mails from postmaster or from
    known trouble-makers.
    """
    department = models.ManyToManyField(
        'service.Department',
        blank=True,
        help_text=_('Leave blank for this e-mail to be ignored on all '
                    'departments, or select those departments you wish to ignore this e-mail '
                    'for.'),
    )

    email_address = models.CharField(
        _('E-Mail Address'),
        max_length=150,
        help_text=_('Enter a full e-mail address, or portions with '
                    'wildcards, eg *@domain.com or postmaster@*.'),
    )

    keep = models.BooleanField(
        _('Keep Emails from blacklisted address?'),
        blank=True,
        default=False,
        help_text=_('Do you want to keep emails from this address in the '
                    'mailbox? If this is not checked, emails from this address will '
                    'be deleted.'),
    )

    def __str__(self):
        return u'%s' % self.name

    def test(self, email):
        """
        Possible situations:
            1. Username & Domain both match
            2. Username is wildcard, domain matches
            3. Username matches, domain is wildcard
            4. username & domain are both wildcards
            5. Other (no match)
            1-4 return True, 5 returns False.
        """

        own_parts = self.email_address.split("@")
        email_parts = email.split("@")

        if self.email_address == email \
                or own_parts[0] == "*" and own_parts[1] == email_parts[1] \
                or own_parts[1] == "*" and own_parts[0] == email_parts[0] \
                or own_parts[0] == "*" and own_parts[1] == "*":
            return True
        else:
            return False

    class Meta:
        verbose_name = _('Blacklisted e-mail address')
        verbose_name_plural = _('Blacklisted e-mail addresses')
        app_label = 'service'