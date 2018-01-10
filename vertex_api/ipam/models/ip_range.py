# IP ranges

# IP addresses can be reserved by adding one or more reserved ranges to a subnet configuration.
# There are two types of ranges that can be defined:
#
# Managed (subnet): no automated system will ever assign IP addresses inside this range. They can
#  be used for anything (e.g. infrastructure systems, network hardware, external DHCP,
# or the namespace for an OpenStack cloud you will be building).
# Unmanaged (subnet): automated systems are using IP addresses inside this range.
from django.db import models

from ipam.constants import AV_CHOICES
from vertex.models import AbstractDatedModel
from netfields import InetAddressField



class IPRange(AbstractDatedModel):

    subnet = models.ForeignKey('ipam.Subnet')
    range_begin = InetAddressField()
    range_end = InetAddressField()

    version = models.PositiveSmallIntegerField(choices=AV_CHOICES, editable=False)

    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.family = self.address.family

        super(IPRange, self).save(*args, **kwargs)