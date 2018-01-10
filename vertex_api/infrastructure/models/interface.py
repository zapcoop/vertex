from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property

from infrastructure.constants import *
from infrastructure.querysets import InterfaceQuerySet


class Interface(models.Model):
    """
    A physical data interface within a Device. An Interface can connect to exactly one other
    Interface via the creation
    of an InterfaceConnection.
    """
    device = models.ForeignKey('Device', related_name='interfaces', on_delete=models.CASCADE)

    mac_address = models.OneToOneField('ipam.MACAddress', blank=True, null=True)

    lag = models.ForeignKey(
        'self',
        models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent LAG'
    )
    name = models.CharField(max_length=64)
    form_factor = models.PositiveSmallIntegerField(choices=IFACE_FF_CHOICES,
                                                   default=IFACE_FF_10GE_SFP_PLUS)
    enabled = models.BooleanField(default=True)
    mtu = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='MTU')
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='OOB Management',
        help_text="This interface is used only for out-of-band management"
    )
    description = models.CharField(max_length=100, blank=True)

    objects = InterfaceQuerySet.as_manager()

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def clean(self):

        # Virtual interfaces cannot be connected
        if self.form_factor in NONCONNECTABLE_IFACE_TYPES and self.is_connected:
            raise ValidationError({
                'form_factor': "Virtual and wireless interfaces cannot be connected to another "
                               "interface or circuit. "
                               "Disconnect the interface or choose a suitable form factor."
            })

        # An interface's LAG must belong to the same device
        if self.lag and self.lag.device != self.device:
            raise ValidationError({
                'lag': "The selected LAG interface ({}) belongs to a different device ({}).".format(
                    self.lag.name, self.lag.device.name
                )
            })

        # A virtual interface cannot have a parent LAG
        if self.form_factor in NONCONNECTABLE_IFACE_TYPES and self.lag is not None:
            raise ValidationError({
                'lag': "{} interfaces cannot have a parent LAG interface.".format(
                    self.get_form_factor_display())
            })

        # Only a LAG can have LAG members
        if self.form_factor != IFACE_FF_LAG and self.member_interfaces.exists():
            raise ValidationError({
                'form_factor':
                    "Cannot change interface form factor; it has LAG members ({}).".format(
                        ", ".join([iface.name for iface in self.member_interfaces.all()])
                    )
            })

    @property
    def is_virtual(self):
        return self.form_factor in VIRTUAL_IFACE_TYPES

    @property
    def is_wireless(self):
        return self.form_factor in WIRELESS_IFACE_TYPES

    @property
    def is_lag(self):
        return self.form_factor == IFACE_FF_LAG

    @property
    def is_connected(self):
        return bool(self.connection)

    @property
    def connection(self):
        try:
            return self.connected_as_near
        except ObjectDoesNotExist:
            pass
        try:
            return self.connected_as_far
        except ObjectDoesNotExist:
            pass
        return None

    @cached_property
    def connected_interface(self):
        try:
            if self.connected_as_near:
                return self.connected_as_near.interface_far
        except ObjectDoesNotExist:
            pass
        try:
            if self.connected_as_far:
                return self.connected_as_far.interface_near
        except ObjectDoesNotExist:
            pass
        return None


class InterfaceConnection(models.Model):
    """
    An InterfaceConnection represents a symmetrical, one-to-one connection between two
    Interfaces. There is no significant difference between the interface_near and interface_far fields.
    """
    interface_near = models.OneToOneField('Interface', related_name='connected_as_near',
                                          on_delete=models.CASCADE)
    interface_far = models.OneToOneField('Interface', related_name='connected_as_far',
                                         on_delete=models.CASCADE)
    connection_status = models.BooleanField(choices=CONNECTION_STATUS_CHOICES,
                                            default=CONNECTION_STATUS_CONNECTED,
                                            verbose_name='Status')

    notes = models.TextField(blank=True)

    def clean(self):
        try:
            if self.interface_near == self.interface_far:
                raise ValidationError({
                    'interface_near': "Cannot connect an interface to itself."
                })
        except ObjectDoesNotExist:
            pass
