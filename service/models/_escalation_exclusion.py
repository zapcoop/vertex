from django.db import models
from django.utils.translation import ugettext_lazy as _
from hvad.models import TranslatableModel, TranslatedFields

from vertex.models import AbstractDatedModel


__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


class EscalationExclusion(AbstractDatedModel, TranslatableModel):
    """
    An 'EscalationExclusion' lets us define a date on which escalation should
    not happen, for example a weekend or public holiday.
    You may also have a Department that is only used on one day per week.
    """

    departments = models.ManyToManyField(
        'service.Department',
        blank=True,
        help_text=_('Leave blank for this exclusion to be applied to all '
                    'departments, or select those departments you wish to exclude with this '
                    'entry.'),
    )

    translations = TranslatedFields(
        name=models.CharField(
            _('Name'),
            max_length=100,

        )
    )

    date = models.DateField(
        _('Date'),
        help_text=_('Date on which escalation should not happen'),
    )

    def __str__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _('Escalation exclusion')
        verbose_name_plural = _('Escalation exclusions')