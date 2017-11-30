import googlemaps

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from places.constants import ADDRESS_TYPES, AUTO_CREATE_PLACES_FOR_TYPES
from places.managers import PlaceManager


class Place(models.Model):
    formatted_address = models.CharField(max_length=200, editable=False)
    related_places = models.ManyToManyField(
        'self',
    )
    point = models.PointField(srid=4326)
    google_place_id = models.CharField(max_length=200, unique=True)
    place_types = ArrayField(
        models.CharField(
            choices=zip(ADDRESS_TYPES, ADDRESS_TYPES),
            max_length=30
        ),
        blank=True,
        null=True
    )
    notes = models.TextField(blank=True)

    objects = PlaceManager()

    @classmethod
    def geocode_raw_address(cls, raw_address):
        gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
        geocode_result = gmaps.geocode(raw_address)
        return geocode_result

    @classmethod
    def geocode_place_id(cls, place_id):
        gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
        place_result = gmaps.place(place_id)
        status = place_result.get('status')
        result = place_result.get('result')
        error_message = place_result.get('error_message')
        if status != "OK":
            if error_message:
                raise ValueError(status + ': ' + error_message)
            else:
                raise ValueError(status)
        return result

    @classmethod
    def get_defaults_from_geocoded_place(cls, geocoded_place, defaults=None):
        point = Point(
            geocoded_place['geometry']['location']['lat'],
            geocoded_place['geometry']['location']['lng']
        )
        if defaults is None: defaults = dict()
        defaults['point'] = point
        defaults['formatted_address'] = geocoded_place['formatted_address']
        defaults['place_types'] = geocoded_place['types']
        return defaults

    def clean(self):
        if self.google_place_id:
            try:
                Place.geocode_place_id(self.google_place_id)
            except ValueError as e:
                raise ValidationError(
                    {
                        "google_place_id": _(
                            "There was an error when processing this ID, "
                            "the error message was '{}'".format(e)
                        )
                    }
                )

    def save(self, *args, **kwargs):
        places_to_create = list()

        if self.pk is not None:
            prev_obj = self.objects.get(pk=self.pk)
            self.google_place_id = prev_obj.google_place_id
            self.point = prev_obj.point
            if self.place_types is None:
                geocoded_place = Place.geocode_place_id(self.google_place_id)
                self.place_types = geocoded_place['types']
        else:
            try:
                geocoded_place = Place.geocode_place_id(self.google_place_id)
            except ValueError as e:
                raise ValueError(
                    _(
                        "There was an error when processing this place ID, "
                        "the error message was '{}'".format(e)
                    )
                )

            defaults = Place.get_defaults_from_geocoded_place(geocoded_place)
            for key, value in defaults.items():
                setattr(self, key, value)

            address_components = geocoded_place['address_components']
            usable_components = list(
                result for result in address_components if not set(result['types']).isdisjoint(
                    AUTO_CREATE_PLACES_FOR_TYPES
                )
            )
            for position in range(len(usable_components)):
                address_component = usable_components[position]
                places_to_create.append(
                    {
                        'raw_address': ', '.join(component['long_name'] for component in
                                                 usable_components[position:]),
                        'place_types': address_component['types']
                    }
                )
                pass

        super(Place, self).save(*args, **kwargs)
        related_places_objects = list()

        for place in places_to_create:
            place, created = Place.objects.get_or_create_from_raw_address(
                raw_address=place['raw_address'], allowed_types=AUTO_CREATE_PLACES_FOR_TYPES)
            related_places_objects.append(place)
            self.related_places.add(place)

        for position in range(len(related_places_objects) - 1):
            place = related_places_objects[position]
            place.related_places.add(related_places_objects[position + 1])

    def __str__(self):
        return self.formatted_address


class CountryManager(PlaceManager):
    def get_queryset(self):
        return super(CountryManager, self).get_queryset().filter(place_types__contains='country')


class Country(Place):
    class Meta:
        proxy = True

    objects = CountryManager()


class LocalityManager(PlaceManager):
    def get_queryset(self):
        return super(LocalityManager, self).get_queryset().filter(place_types__contains='locality')


class Locality(Place):
    class Meta:
        proxy = True

    objects = LocalityManager()

class SubLocalityManager(PlaceManager):
    def get_queryset(self):
        return super(SubLocalityManager, self).get_queryset().filter(place_types__contains='sublocality')


class SubLocality(Place):
    class Meta:
        proxy = True

    objects = SubLocalityManager()
