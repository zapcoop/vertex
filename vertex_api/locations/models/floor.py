from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from locations.models import Room
from vertex.models import AbstractDatedModel


class Floor(AbstractDatedModel):
    class Meta:
        ordering = ['number']
        verbose_name = _("Floor")
        verbose_name_plural = _("Floors")
        # unique_together = (('label', 'location'),)

    label = models.CharField(
        _("Floor label"),
        max_length=30,
        help_text=_("Enter the label for this floor just as it would appear in an elevator "
                    "or on fire escape plans.")
    )
    number = models.IntegerField(
        _("Number"),
        help_text=_("Enter the floor number relative to ground level. Ground level equals 0.")
    )
    elevation = models.FloatField(
        blank=True,
        null=True,
        help_text=_("Enter the elevation in meters above sea level.")
    )

    location = models.ForeignKey('locations.Location')

    place = models.OneToOneField(
        'places.Place',
        limit_choices_to={'place_type': 'floor'},
        blank=True,
        null=True
    )

    # premise = models.ForeignKey(
    #     'places.Place',
    #     limit_choices_to=Q(place_type='establishment') | Q(place_type='street_number') | Q(place_type='street_address')| Q(place_type='premise'),
    #
    #     blank=True,
    #     null=True
    # )

    def clean(self):
        errors = {}
        try:
            room = Room.objects.get(id=self.id)
        except Room.DoesNotExist:
            pass
        else:
            if self.room_set.count() != 0:
                if room.label != self.label:
                    errors.update(
                        {'label': [_('You cannot change the floor label if it is not empty.')]}
                    )
                if room.place != self.place:
                    errors.update(
                        {
                            'location': [
                                _('You cannot change the floor location if it is not empty.')]
                        }
                    )
        if self.location_id and not self.location.label_text:
            errors.update(
                {
                    'floor': [mark_safe(_('This floor location has no label text configured.<br>'
                                          'Please fix the location label text...'))]
                }
            )
        if errors:
            raise ValidationError(errors)
