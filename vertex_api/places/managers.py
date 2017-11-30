from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class PlaceManager(models.GeoManager):
    def get_or_create_from_raw_address(self,
                                       raw_address,
                                       allowed_types=settings.GMAPS_ALLOWED_LOCATION_TYPES,
                                       defaults=None,
                                       **kwargs):
        from places.models import Place

        geocode_result = Place.geocode_raw_address(raw_address)

        filtered_results = list(
            result for result in geocode_result if
            not set(result['types']).isdisjoint(
                allowed_types
            )
        )
        if len(filtered_results) == 0:
            raise ValueError(
                _(
                    "There are no results when geocoding '{raw_address}' with the "
                    "allowed types '{types}'".format(raw_address=raw_address,
                                                     types=", ".join(allowed_types))
                )
            )
        geocoded_place = filtered_results[0]
        google_place_id = geocoded_place['place_id']
        defaults = Place.get_defaults_from_geocoded_place(geocoded_place, defaults)
        place, created = self.get_or_create(google_place_id=google_place_id,
                                            defaults=defaults,
                                            **kwargs)

        return (place, created)

    def get_or_create_from_place_id(self, place_id, defaults=None, **kwargs):
        from places.models import Place

        try:
            geocoded_place = Place.geocode_place_id(place_id)
        except ValueError as e:
            raise ValueError(
                _(
                    "There was an error when processing this ID, "
                    "the error message was '{}'".format(e)
                )
            )

        google_place_id = geocoded_place['place_id']
        defaults = Place.get_defaults_from_geocoded_place(geocoded_place, defaults)
        place, created = self.get_or_create(google_place_id=google_place_id,
                                            defaults=defaults,
                                            **kwargs)

        return (place, created)
