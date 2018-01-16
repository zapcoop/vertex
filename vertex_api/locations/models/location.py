from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from places.models import Place
from vertex.models import AbstractDatedModel


class Location(AbstractDatedModel):
    raw_address = models.CharField(max_length=200, null=True, blank=True)
    place = models.ForeignKey(
        'places.Place',
        editable=False,
        limit_choices_to={'place_type': settings.GMAPS_ALLOWED_LOCATION_TYPES},
        blank=True,
        null=True
    )
    formatted_address = models.CharField(max_length=200, null=True, blank=True, editable=False)
    notes = models.TextField(null=True, blank=True)

    def clean(self):
        if not self.place:
            geocode_result = Place.geocode_raw_address(self.raw_address)
            filtered_results = list(
                result for result in geocode_result if
                not set(result['types']).isdisjoint(
                    settings.GMAPS_ALLOWED_LOCATION_TYPES
                )
            )
            if len(filtered_results) == 0:
                raise ValidationError(
                    {
                        "raw_address": _(
                            "There are no results when geocoding '{raw_address}' with the "
                            "allowed types".format(raw_address=self.raw_address)
                        )
                    }
                )
            elif len(filtered_results) != 1:
                raise ValidationError(
                    {
                        "raw_address": _(
                            "There is more than one result when geocoding '{raw_address}' with the "
                            "allowed types, be more specific".format(raw_address=self.raw_address)
                        )
                    }
                )
            geocoded_place = filtered_results[0]
            google_place_id = geocoded_place['place_id']
            place, created = Place.objects.get_or_create_from_place_id(google_place_id)
            self.place = place
            self.formatted_address = self.place.formatted_address


def save(self, *args, **kwargs):
    if not self.place:
        place, created = Place.objects.get_or_create_from_raw_address(
            self.raw_address,
            allowed_types=settings.GMAPS_ALLOWED_LOCATION_TYPES
        )
        self.place = place
    self.formatted_address = self.place.formatted_address
    super(Location, self).save(*args, **kwargs)


def __str__(self):
    return self.formatted_address


class Meta:
    pass
