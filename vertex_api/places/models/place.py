import googlemaps

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from places.constants import ADDRESS_TYPES
from places.models import AddressComponent, AddressComponentThrough


class Place(models.Model):
    raw_address = models.CharField(max_length=200, null=True, blank=True)
    formatted_address = models.CharField(max_length=200, editable=False)
    address_components = models.ManyToManyField(
        'AddressComponent',
        through="AddressComponentThrough"
    )
    point = models.PointField(srid=4326)
    google_place_id = models.CharField(max_length=200, unique=True, blank=True)
    place_type = models.CharField(
        choices=zip(ADDRESS_TYPES, ADDRESS_TYPES),
        max_length=30
    )
    notes = models.TextField(blank=True)

    @cached_property
    def geocoded_raw_address(self):
        if self.raw_address:
            gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
            geocode_result = gmaps.geocode(self.raw_address)
            return geocode_result
        return None

    @cached_property
    def geocoded_place_id(self):
        if self.raw_address:
            gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
            place_result = gmaps.place(self.google_place_id)
            status = place_result.get('status')
            result = place_result.get('result')
            error_message = place_result.get('error_message')
            if status != "OK":
                if error_message:
                    raise ValueError(status + ': ' + error_message)
                else:
                    raise ValueError(status)
            return result
        return None

    def clean(self):
        if self.google_place_id:
            try:
                place = self.geocoded_place_id
            except ValueError as e:
                raise ValidationError(
                    {
                        "google_place_id": _(
                            "There was an error when processing this ID, "
                            "the error message was '{}'".format(e)
                        )
                    }
                )

        elif self.raw_address:
            geocode_result = self.geocoded_raw_address
            filtered_results = list(result for result in geocode_result if
                                    self.place_type in result["types"])
            if len(geocode_result) == 0:
                raise ValidationError(
                    _(
                        "There are no results when geocoding he entered address with the selected "
                        "type"
                    ))
            elif len(filtered_results) != 1:
                raise ValidationError(
                    {
                        "raw_address": _(
                            "There is more than one result when geocoding the entered address "
                            "with the selected type, please be more specific"
                        )
                    }
                )

        else:
            raise ValidationError(
                _(
                    "Either 'Raw address' or 'Google place ID' must be submitted, both cannot be "
                    "left blank"
                )

            )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            prev_obj = self.objects.get(pk=self.pk)
            self.raw_address = prev_obj.raw_address
            self.google_place_id = prev_obj.google_place_id
            self.lat_long = prev_obj.lat_long
        else:
            if self.google_place_id:
                place = self.geocoded_place_id

            elif self.raw_address:
                geocode_result = self.geocoded_raw_address
                filtered_results = list(result for result in geocode_result if
                                        self.place_type in result["types"])
                if len(geocode_result) == 0:
                    raise ValueError(
                        _(
                            "There are no results when geocoding the entered address with the "
                            "selected type"
                        ))
                elif len(filtered_results) != 1:
                    raise ValueError(
                        _(
                            "There is more than one result when geocoding the entered address "
                            "with the selected type, please be more specific"
                        )
                    )
                place = filtered_results[0]
            else:
                raise ValueError(
                    _(
                        "Either 'raw_address' or 'google_place_id' must be have a value, "
                        "both cannot be left blank"
                    )

                )

            self.point = Point(
                place['geometry']['location']['lat'],
                place['geometry']['location']['lng']
            )
            self.google_place_id = place['place_id']
            self.formatted_address = place['formatted_address']

        super(Place, self).save(*args, **kwargs)

        order = 0
        for component in place['address_components']:
            component_types = component['types']

            address_component, created = AddressComponent.objects.get_or_create(
                short_name=component['short_name'],
                long_name=component['long_name'],
                component_type=component_types[0]
            )
            AddressComponentThrough.objects.create(
                address_component=address_component,
                place=self,
                order=order
            )
            order += 1

    def __str__(self):
        return self.formatted_address

    class Meta:
        pass
