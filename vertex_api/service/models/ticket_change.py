from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
__author__ = 'Jonathan Senecal <jonathan@zap.coop>'


class TicketChange(models.Model):
    """
    For each Note, any changes to the parent ticket (eg Title, Priority,
    etc) are tracked here for display purposes.
    """

    update = models.ForeignKey('service.Update')

    field = models.CharField(
        _('Field'),
        max_length=100,
    )

    old_value = models.TextField(
        _('Old Value'),
        blank=True,
        null=True,
    )

    new_value = models.TextField(
        _('New Value'),
        blank=True,
        null=True,
    )

    def __str__(self):
        str = u'%s ' % self.field
        if not self.new_value:
            str += ugettext('removed')
        elif not self.old_value:
            str += ugettext('set to %s') % self.new_value
        else:
            str += ugettext('changed from "%(old_value)s" to "%(new_value)s"') % {
                'old_value': self.old_value,
                'new_value': self.new_value
            }
        return str

    class Meta:
        verbose_name = _('Ticket change')
        verbose_name_plural = _('Ticket changes')
