from django.db import models
from django.utils.translation import ugettext_lazy as _

from vertex.models import AbstractDatedModel


class Room(AbstractDatedModel):
    class Meta:
        ordering = ['floor']
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        # unique_together = ('label_text', 'floor')

    floor = models.ForeignKey('locations.Floor')
    # subpremise = models.ForeignKey
    label = models.CharField(
        _("Floor label"),
        max_length=30,
        help_text=_(
            "Enter the label for this room just as it is found in that location or create one "
            "using alphanumeric characters.")
    )
    place = models.ForeignKey(
        'places.Place',
        editable=False,
        limit_choices_to={'place_type': 'room'},
        blank=True,
        null=True
    )
    notes = models.TextField(null=True, blank=True)
