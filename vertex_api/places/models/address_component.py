from django.db import models

from places.constants import ADDRESS_COMPONENT_TYPES


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
        return "{}: {}".format(self.component_type.capitalize(), self.long_name)

    class Meta:
        unique_together = (
            ('long_name', 'short_name')
        )


class RouteManager(models.Manager):
    def get_queryset(self):
        return super(RouteManager, self).get_queryset().filter(component_type='route')


class Route(AddressComponent):
    class Meta:
        proxy = True

    objects = RouteManager()

    def save(self, *args, **kwargs):
        self.component_type = 'route'
        super().save(*args, **kwargs)


class CountryManager(models.Manager):
    def get_queryset(self):
        return super(CountryManager, self).get_queryset().filter(component_type='country')


class Country(AddressComponent):
    class Meta:
        proxy = True

    objects = CountryManager()

    def save(self, *args, **kwargs):
        self.component_type = 'country'
        super().save(*args, **kwargs)


class LocalityManager(models.Manager):
    def get_queryset(self):
        return super(LocalityManager, self).get_queryset().filter(component_type='locality')


class Locality(AddressComponent):
    class Meta:
        proxy = True

    objects = LocalityManager()

    def save(self, *args, **kwargs):
        self.component_type = 'locality'
        super().save(*args, **kwargs)
