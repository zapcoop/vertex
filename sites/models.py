import googlemaps
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

ADDRESS_COMPONENT_TYPES = (
    'street_address',  # indicates a precise street address.
    'route',  # indicates a named route (such as "US 101").
    'intersection',  # indicates a major intersection, usually of two major roads.
    'political',
    # indicates a political entity. Usually, this type indicates a polygon of some civil administration.
    'country',
    # indicates the national political entity, and is typically the highest order type returned by the Geocoder.
    'administrative_area_level_1',
    # indicates a first-order civil entity below the country level. Within the United States, these administrative levels are states. Not all nations exhibit these administrative levels. In most cases, administrative_area_level_1 short names will closely match ISO 3166-2 subdivisions and other widely circulated lists; however this is not guaranteed as our geocoding results are based on a variety of signals and location data.
    'administrative_area_level_2',
    # indicates a second-order civil entity below the country level. Within the United States, these administrative levels are counties. Not all nations exhibit these administrative levels.
    'administrative_area_level_3',
    # indicates a third-order civil entity below the country level. This type indicates a minor civil division. Not all nations exhibit these administrative levels.
    'administrative_area_level_4',
    # indicates a fourth-order civil entity below the country level. This type indicates a minor civil division. Not all nations exhibit these administrative levels.
    'administrative_area_level_5',
    # indicates a fifth-order civil entity below the country level. This type indicates a minor civil division. Not all nations exhibit these administrative levels.
    'colloquial_area',  # indicates a commonly-used alternative name for the entity.
    'locality',  # indicates an incorporated city or town political entity.
    'sublocality',
    # indicates a first-order civil entity below a locality. For some locations may receive one of the additional types: sublocality_level_1 to sublocality_level_5. Each sublocality level is a civil entity. Larger numbers indicate a smaller geographic area.
    'neighborhood',  # indicates a named neighborhood
    'premise',
    # indicates a named location, usually a building or collection of buildings with a common name
    'subpremise',
    # indicates a first-order entity below a named location, usually a singular building within a collection of buildings with a common name
    'postal_code',  # indicates a postal code as used to address postal mail within the country.
    'natural_feature',  # indicates a prominent natural feature.
    'airport',  # indicates an airport.
    'park',  # indicates a named park.
    'point_of_interest',
    # indicates a named point of interest. Typically, these "POI"s are prominent local entities that don't easily fit in another category, such as "Empire State Building" or "Statue of Liberty."
)

ADDRESS_TYPES = ADDRESS_COMPONENT_TYPES + (
    'floor',  # indicates the floor of a building address.
    'establishment',  # typically indicates a place that has not yet been categorized.
    'parking',  # indicates a parking lot or parking structure.
    'post_box',  # indicates a specific postal box.
    'postal_town',
    # indicates a grouping of geographic areas, such as locality and sublocality, used for mailing addresses in some countries.
    'room',  # indicates the room of a building address.
    'street_number',  # indicates the precise street number.
    'bus_station',
    'train_station',
    'transit_station',  # indicate the location of a bus, train or public transit stop.
)


class AddressComponentThrough(models.Model):
    place = models.ForeignKey('Place')
    address_component = models.ForeignKey('AddressComponent')
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = (('place', 'order'),)


class AddressComponent(models.Model):
    long_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)

    component_type = models.CharField(
        choices=zip(ADDRESS_COMPONENT_TYPES, ADDRESS_COMPONENT_TYPES),
        max_length=30,
        editable=False
    )

    def __str__(self):
        return "{}, {}".format(self.component_type, self.long_name)

    class Meta:
        unique_together = (
            ('long_name', 'short_name')
        )


class Place(models.Model):
    raw_address = models.CharField(max_length=200, null=True, blank=True)
    formatted_address = models.CharField(max_length=200, editable=False)
    address_components = models.ManyToManyField(
        'AddressComponent',
        through="AddressComponentThrough"
    )
    lat_long = models.PointField(srid=4326)
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
                    {"google_place_id": _(
                        "There was an error when processing this ID, the error message was '{}'".format(
                            e)
                    )}
                )

        elif self.raw_address:
            geocode_result = self.geocoded_raw_address
            filtered_results = list(result for result in geocode_result if
                                    self.place_type in result["types"])
            if len(geocode_result) == 0:
                raise ValidationError(
                    _(
                        "There are no results when geocoding he entered address with the selected type"
                    ))
            elif len(filtered_results) != 1:
                raise ValidationError(
                    {"raw_address": _(
                        "There is more than one result when geocoding the entered address with the selected type, please be more specific"
                    )}
                )

        else:
            raise ValidationError(
                _(
                    "Either 'Raw address' or 'Google place ID' must be submitted, both cannot be left blank"
                )

            )

    def save(self, *args, **kwargs):
        global place
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
                            "There are no results when geocoding the entered address with the selected type"
                        ))
                elif len(filtered_results) != 1:
                    raise ValueError(
                        _(
                            "There is more than one result when geocoding the entered address with the selected type, please be more specific"
                        )
                    )
                place = filtered_results[0]
            else:
                raise ValueError(
                    _(
                        "Either 'raw_address' or 'google_place_id' must be have a value, both cannot be left blank"
                    )

                )

            self.lat_long = Point(
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
