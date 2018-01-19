# IP ranges

# IP addresses can be reserved by adding one or more reserved ranges to a subnet configuration.
# There are two types of ranges that can be defined:
#
# Managed: no automated system will ever assign IP addresses inside this range. They can
#  be used for anything (e.g. infrastructure systems, network hardware, external DHCP, etc.
# Unmanaged: automated systems are using IP addresses inside this range.
import netaddr
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.db import models
from netaddr import IPNetwork

from ipam.constants import AV_CHOICES
from vertex.models import AbstractDatedModel
from netfields import InetAddressField


class IPRangeRole(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    color = ColorField()
    managed = models.BooleanField(
        default=True,
        help_text="When true, no automated system will ever assign IP addresses inside this "
                  "range. They can be used for anything (e.g. infrastructure systems, "
                  "network hardware, external DHCP, etc."
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class IPRange(AbstractDatedModel):
    subnet = models.ForeignKey('ipam.Subnet')
    range_begin = InetAddressField(store_prefix_length=False)
    range_end = InetAddressField(store_prefix_length=False)

    version = models.PositiveSmallIntegerField(choices=AV_CHOICES, editable=False)

    role = models.ForeignKey('ipam.IPRangeRole', blank=True, null=True)

    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def clean(self):
        field_errors = {}

        # range is reversed
        if self.range_begin > self.range_end:
            raise ValidationError(
                _("Proposed range is reversed"),
                code='reversed_range'
            )

        netaddr_cidr = IPNetwork(str(self.subnet.cidr))

        if int(self.range_begin) < netaddr_cidr.first:
            field_errors.update({
                'range_begin':
                    ValidationError(_(
                        '%(begin)s is smaller than %(subnet)s first possible address (%(address)s)'
                    ),
                        params={
                            'begin': self.range_begin,
                            'subnet': netaddr_cidr,
                            'address': netaddr_cidr.network
                        },
                        code='invalid_begin_value'
                    )
            })

        if int(self.range_end) > netaddr_cidr.last:
            field_errors.update({
                'range_end':
                    ValidationError(_(
                        '%(end)s is greater than %(subnet)s last possible address (%(address)s)'
                    ),
                        params={
                            'end': self.range_end,
                            'subnet': netaddr_cidr,
                            'address': netaddr_cidr.broadcast
                        },
                        code='invalid_end_value'
                    )
            })

        if field_errors:
            raise ValidationError(field_errors)
        subnets_in_range = self.subnets_in_range.filter(supernet=self.subnet)
        if subnets_in_range.exists():
            raise ValidationError(
                _("Range %(range)s clashes with subnet(s) %(subnet)s"),
                code="conflict_with_subnet",
                params={
                    'range': self.range,
                    'subnet': ", ".join((str(s) for s in subnets_in_range))
                }
            )

    @property
    def subnets_in_range(self):
        from ipam.models import Subnet
        contains_or_eq_begin = Q(cidr__net_contains_or_equals=self.range_begin)
        contains_or_eq_end = Q(cidr__net_contains_or_equals=self.range_end)
        in_range = Q(cidr__range=(self.range.first, self.range.last))
        return Subnet.objects.filter(
            Q(contains_or_eq_begin | contains_or_eq_end | in_range)
        )

    @property
    def range(self):
        return netaddr.IPRange(str(self.range_begin), str(self.range_end))

    @range.setter
    def range(self, value):
        self.range_begin = value[0]
        self.range_end = value[-1]

    def save(self, *args, **kwargs):
        self.version = self.range.version

        if self.range_begin > self.range_end:
            raise ValueError("Proposed range is reversed")

        netaddr_cidr = IPNetwork(str(self.subnet.cidr))

        if int(self.range_begin) < netaddr_cidr.first:
            raise ValueError(
                '%(begin)s is smaller than %(subnet)s first possible address (%(address)s)' % {
                    'begin': self.range_begin,
                    'subnet': netaddr_cidr,
                    'address': netaddr_cidr.network
                }
            )

        if int(self.range_end) > netaddr_cidr.last:
            raise ValueError(
                '%(end)s is greater than %(subnet)s last possible address (%(address)s)' % {
                    'end': self.range_end,
                    'subnet': netaddr_cidr,
                    'address': netaddr_cidr.broadcast
                }
            )

        subnets_in_range = self.subnets_in_range.filter(supernet=self.subnet)
        if subnets_in_range.exists():
            raise ValueError(
                "Range %(range)s clashes with subnet(s) %(subnet)s" % {
                    'range': self.range,
                    'subnet': ", ".join((str(s) for s in subnets_in_range))
                }
            )

        super(IPRange, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.range)
