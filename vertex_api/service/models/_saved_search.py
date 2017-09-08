from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields

from vertex.models import AbstractDatedModel


__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


class SavedSearch(AbstractDatedModel, TranslatableModel):
    """
    Allow a user to save a ticket search, eg their filtering and sorting
    options, and optionally share it with other users. This lets people
    easily create a set of commonly-used filters, such as:
        * My tickets waiting on me
        * My tickets waiting on submitter
        * My tickets in 'Priority Support' queue with priority of 1
        * All tickets containing the word 'billing'.
         etc...
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
    )

    translations = TranslatedFields(
        title=models.CharField(
            _('Query Name'),
            max_length=100,
            help_text=_('User-provided name for this query'),
        ),
    )

    shared = models.BooleanField(
        _('Shared With Other Users?'),
        blank=True,
        default=False,
        help_text=_('Should other users see this query?'),
    )

    query = models.TextField(
        _('Search Query'),
        help_text=_('Pickled query object. Be wary changing this.'),
    )

    def __str__(self):
        if self.shared:
            return u'%s (*)' % self.title
        else:
            return u'%s' % self.title

    class Meta:
        verbose_name = _('Saved search')
        verbose_name_plural = _('Saved searches')
        app_label = 'service'