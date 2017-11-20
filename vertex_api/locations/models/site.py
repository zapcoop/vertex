from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string

from django.utils.translation import ugettext_lazy as _

from vertex.managers import NaturalOrderByManager
from vertex.models import AbstractDatedModel


class SiteManager(NaturalOrderByManager):
    def get_queryset(self):
        return self.natural_order_by('name')


class Site(AbstractDatedModel):
    """
    A Site represents a geographic location within a network; typically a building or campus.
    The optional facility field can be used to include an external designation,
    such as a data center name (e.g. Equinix TR1).
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    site_tag = models.SlugField(
        max_length=8,
        verbose_name=_('Site tag'),
        editable=False,
        unique=True
    )

    facility = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Used to include an external designation such as a data center name (e.g. Equinix TR1)"
        )
    )

    places = models.ManyToManyField('places.Place')

    notes = models.TextField(blank=True)

    objects = SiteManager()

    class Meta:
        ordering = ['name']

    def generate_site_tag(self):
        if self.pk is None and not self.site_tag:
            site_tag = "S-" + get_random_string(settings.VERTEX_TAG_LEN, settings.VERTEX_TAG_CHARS)
            if self.__class__.objects.filter(site_tag=site_tag).exists():
                self.generate_site_tag()
            else:
                self.site_tag = site_tag

    def save(self, *args, **kwargs):
        self.generate_site_tag()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
