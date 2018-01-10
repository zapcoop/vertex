from django.db import models

from infrastructure.models import Interface
from ipam.constants import AV_CHOICES, IPADDRESS_STATUS_CHOICES, IPADDRESS_STATUS_ACTIVE, \
    IPADDRESS_ROLE_CHOICES
from vertex.models import AbstractDatedModel
from netfields import InetAddressField


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

    subnet = models.ForeignKey('ipam.Subnet')
    address = InetAddressField()

    version = models.PositiveSmallIntegerField(choices=AV_CHOICES, editable=False)

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
        self.version = self.address.version

        super(IPAddress, self).save(*args, **kwargs)



    class Meta:
        ordering = ['family', 'address']
        verbose_name = 'IP address'
        verbose_name_plural = 'IP addresses'

    def __str__(self):
        return str(self.address)

    def get_absolute_url(self):
        return reverse('ipam:ipaddress', args=[self.pk])

    def get_duplicates(self):
        return IPAddress.objects.filter(vrf=self.vrf,
                                        address__net_host=str(self.address.ip)).exclude(
            pk=self.pk)

    def clean(self):

        if self.address:

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

    @property
    def virtual_machine(self):
        if self.interface:
            return self.interface.virtual_machine
        return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]

    def get_role_class(self):
        return ROLE_CHOICE_CLASSES[self.role]
