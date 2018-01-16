from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.functional import cached_property

from ipam.constants import AV_CHOICES, IPADDRESS_STATUS_CHOICES, IPADDRESS_STATUS_ACTIVE, \
    IPADDRESS_ROLE_CHOICES, STATUS_CHOICE_CSS, ROLE_CHOICE_CSS
from ipam.models import Subnet
from vertex.models import AbstractDatedModel
from netfields import InetAddressField
import netaddr


class IPAddress(AbstractDatedModel):
    """
    An IPAddress represents an individual IPv4 or IPv6 address and its mask.

    An IPAddress can optionally be assigned to an Interface.
    Interfaces can have zero or more IPAddresses assigned to them.

    An IPAddress can also optionally point to a NAT inside IP, designating itself as a
    NAT outside IP. This is useful, for example, when mapping public addresses to private addresses.
    When an Interface has been assigned an IPAddress which has a NAT outside IP, that Interface's
    Device can use either the inside or outside IP as its primary IP.
    """

    subnet = models.ForeignKey('ipam.Subnet', editable=False)
    address = InetAddressField()
    version = models.PositiveSmallIntegerField(choices=AV_CHOICES, editable=False)

    interface = models.ForeignKey('infrastructure.Interface', blank=True, null=True)

    status = models.PositiveSmallIntegerField(
        'Status', choices=IPADDRESS_STATUS_CHOICES, default=IPADDRESS_STATUS_ACTIVE,
        help_text='The operational status of this IP'
    )
    role = models.PositiveSmallIntegerField(
        'Role', choices=IPADDRESS_ROLE_CHOICES, blank=True, null=True,
        help_text='The functional role of this IP'
    )

    nat_inside = models.OneToOneField('self', related_name='nat_outside',
                                      on_delete=models.SET_NULL, blank=True,
                                      null=True, verbose_name='NAT (Inside)',
                                      help_text="The IP for which this address is the \"outside\" "
                                                "IP")

    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):

        if not isinstance(self.address, netaddr.IPAddress):
            self.address = netaddr.IPAddress(self.address)

        self.version = self.address.version

        self.subnet = self.find_parent()


        super(IPAddress, self).save(*args, **kwargs)

    def find_parent(self):
        return Subnet.objects.filter(cidr__net_contains=self.address).order_by('-cidr').first()

    class Meta:
        ordering = ['version', 'address']
        verbose_name = 'IP address'
        verbose_name_plural = 'IP addresses'

    @cached_property
    def vrf(self):
        return self.subnet.vrf

    def __str__(self):
        return str(self.address)

    def get_duplicates(self):
        return IPAddress.objects.filter(subnet=self.subnet,
                                        address=self.address).exclude(
            pk=self.pk)

    def clean(self):

        if self.address:
            # Find parent subnet
            self.subnet = self.find_parent()

            # Enforce unique IP space (if applicable)
            if (self.vrf is None and settings.ENFORCE_GLOBAL_UNIQUE) or (
                    self.vrf and self.vrf.enforce_unique):
                duplicate_ips = self.get_duplicates()
                if duplicate_ips:
                    raise ValidationError({
                        'address': "Duplicate IP address found in {}: {}".format(
                            "VRF {}".format(self.vrf) if self.vrf else "global table",
                            duplicate_ips.first(),
                        )
                    })

    @property
    def device(self):
        if self.interface:
            return self.interface.device
        return None


    def get_status_class(self):
        return STATUS_CHOICE_CSS[self.status]

    def get_role_class(self):
        return ROLE_CHOICE_CSS[self.role]
