from django.db import models
from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields

from vertex.models import AbstractDatedModel


__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


class ReplyTemplate(AbstractDatedModel, TranslatableModel):
    """
    We can allow the admin to define a number of pre-set replies, used to
    simplify the sending of updates and resolutions. These are basically Django
    templates with a limited context - however if you wanted to get crafy it would
    be easy to write a reply that displays ALL updates in hierarchical order etc
    with use of for loops over {{ ticket.followup_set.all }} and friends.
    When replying to a ticket, the user can select any reply set for the current
    department, and the body text is fetched via AJAX.
    """

    departments = models.ManyToManyField(
        'service.department',
        blank=True,
        help_text=_('Leave blank to allow this reply to be used for all '
                    'departments, or select those departments you wish to limit this reply to.'),
    )

    translations = TranslatedFields(
        name=models.CharField(
            _('Name'),
            max_length=100,
            help_text=_('Only used to assist users with selecting a reply - not '
                        'shown to the user.'),
        ),
        body=models.TextField(
            _('Body'),
            help_text=_('Context available: {{ ticket }} - ticket object (eg '
                        '{{ ticket.title }}); {{ department }} - The department; and {{ user }} '
                        '- the current user.'),
        )

    )

    class Meta:
        ordering = ['translations__name', ]
        verbose_name = _('Pre-set reply')
        verbose_name_plural = _('Pre-set replies')
        app_label = 'service'

    def __str__(self):
        return u'%s' % self.name