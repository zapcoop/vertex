from django.db import models

from vertex.models import AbstractDatedModel


class VRF(AbstractDatedModel):
    """
    A virtual routing and forwarding (VRF) table represents a discrete layer three forwarding
    domain (e.g. a routing table). Prefixes and IPAddresses can optionally be assigned to VRFs.
    (Subnets that are not assigned to a VRF are said to exist in the "global" table.)
    """
    name = models.CharField(max_length=50)
    rd = models.CharField(max_length=21, unique=True, verbose_name='Route distinguisher')
    space = models.ForeignKey('ipam.Space')
    enforce_unique = models.BooleanField(default=True, verbose_name='Enforce unique space',
                                         help_text="Prevent duplicate prefixes/IP addresses "
                                                   "within this VRF")
    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'VRF'
        verbose_name_plural = 'VRFs'

    def __str__(self):
        return self.display_name or super(VRF, self).__str__()

    def get_absolute_url(self):
        return reverse('ipam:vrf', args=[self.pk])

    def to_csv(self):
        return csv_format([
            self.name,
            self.rd,
            self.tenant.name if self.tenant else None,
            self.enforce_unique,
            self.description,
        ])

    @property
    def display_name(self):
        if self.name and self.rd:
            return "{} ({})".format(self.name, self.rd)
        return None
