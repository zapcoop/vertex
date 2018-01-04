# Heavily inspired from https://github.com/digitalocean/netbox/

from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from netmiko.ssh_dispatcher import CLASS_MAPPER

from infrastructure.constants import *
from infrastructure.managers import DeviceManager, PowerOutletManager
from infrastructure.models import Interface
from vertex.models import AbstractDatedModel


class DeviceRole(models.Model):
    """
    Devices are organized by functional role; for example, "Core Switch" or "File Server". Each
    DeviceRole is assigned a
    color to be used when displaying rack elevations.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    color = ColorField()

    class Meta:
        app_label = 'infrastructure'
        ordering = ['name']

    def __str__(self):
        return self.name


class Platform(models.Model):
    """
    Platform refers to the software or firmware running on a Device; for example, "Cisco IOS-XR"
    or "Juniper Junos".
    Vertex uses Platforms to determine how to interact with devices when pulling inventory data
    or other information.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    netmiko_type = models.CharField(
        max_length=50,
        choices=((v, k) for k, v in CLASS_MAPPER.items()),
        blank=True,
        verbose_name='Netmiko device type',
        help_text="The name of the Netmiko device type to use when interacting with devices of "
                  "this platform."
    )

    class Meta:
        app_label = 'infrastructure'
        ordering = ['name']

    def __str__(self):
        return self.name


class Device(AbstractDatedModel):
    """
    A Device represents a piece of physical hardware. Each Device is linked to a DeviceDefinition,
    DeviceRole, and (optionally) a Platform. Device names are not required, however if one is set
    it must be unique.

    Each Device must be assigned to a site, and optionally to a rack within that site.
    Associating a device with a particular rack face or unit is optional
    (for example, vertically mounted PDUs do not consume rack units).

    When a new Device is created, serial/power/interface/device bay components are created along
    with it as dictated by the component templates assigned to its DeviceDefinition.
    Components can also be added, modified, or deleted after the creation of a Device.
    """
    device_definition = models.ForeignKey(
        'infrastructure.DeviceDefinition',
        related_name='instances',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    device_role = models.ForeignKey(
        'infrastructure.DeviceRole',
        related_name='devices',
        on_delete=models.PROTECT
    )
    asset = models.ForeignKey(
        'inventory.Asset',
        blank=True,
        null=True,
        related_name='devices',
        on_delete=models.PROTECT
    )
    platform = models.ForeignKey(
        'infrastructure.Platform',
        related_name='devices',
        blank=True, null=True,
        on_delete=models.SET_NULL
    )
    name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True
    )

    location = models.ForeignKey(
        'locations.Location',
        related_name='devices',
        on_delete=models.PROTECT
    )

    room = models.ForeignKey(
        'locations.Room',
        related_name='devices',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    wall = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        choices=SIDES,
        verbose_name=_('Wall')
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status'
    )

    # TODO: ADD IP ADDRESSES FK
    # primary_ip4 = models.OneToOneField(
    #     'ipam.IPAddress', related_name='primary_ip4_for', on_delete=models.SET_NULL, blank=True,
    #     null=True,
    #     verbose_name='Primary IPv4'
    # )
    # primary_ip6 = models.OneToOneField(
    #     'ipam.IPAddress', related_name='primary_ip6_for', on_delete=models.SET_NULL, blank=True,
    #     null=True,
    #     verbose_name='Primary IPv6'
    # )
    notes = models.TextField(blank=True)

    objects = DeviceManager()

    class Meta:
        app_label = 'infrastructure'
        ordering = ['name']
        permissions = (
            ('netmiko_read', 'Read-only access to devices via netmiko'),
            ('netmiko_write', 'Read/write access to devices via netmiko'),
        )

    def __str__(self):
        return self.display_name or super(Device, self).__str__()

    def clean(self):
        # Validate location/room combination
        if self.room and self.location != self.room.floor.location:
            raise ValidationError({
                'room': "Room {} does not belong to location {}.".format(self.room, self.location),
            })

        if not self.room and self.wall is not None:
            raise ValidationError({
                'wall': "Cannot select a room wall without assigning a room.",
            })

        if not self.device_definition and not self.asset:
            raise ValidationError("Either an Asset of a device definition must be selected.")

        if self.asset:
            if not self.asset.item.devicedefinition:
                raise ValidationError({
                    'asset': "Asset {} item has no configured device definition".format(self.asset),
                })
            else:
                self.device_definition = self.asset.item.devicedefinition

        # # Validate primary IPv4 address
        # if self.primary_ip4 and (
        #                 self.primary_ip4.interface is None or
        #                 self.primary_ip4.interface.device != self
        # ) and (
        #                 self.primary_ip4.nat_inside.interface is None or
        #                 self.primary_ip4.nat_inside.interface.device != self
        # ):
        #     raise ValidationError({
        #         'primary_ip4': "The specified IP address ({}) is not assigned to this "
        #                        "device.".format(
        #             self.primary_ip4),
        #     })
        #
        # # Validate primary IPv6 address
        # if self.primary_ip6 and (
        #                 self.primary_ip6.interface is None or
        #                 self.primary_ip6.interface.device != self
        # ) and (
        #                 self.primary_ip6.nat_inside.interface is None or
        #                 self.primary_ip6.nat_inside.interface.device != self
        # ):
        #     raise ValidationError({
        #         'primary_ip6': "The specified IP address ({}) is not assigned to this "
        #                        "device.".format(
        #             self.primary_ip6),
        #     })

    def save(self, *args, **kwargs):
        is_new = not bool(self.pk)

        super(Device, self).save(*args, **kwargs)

        # If this is a new Device, instantiate all of the related components per the DeviceType
        # definition
        if is_new and self.device_definition:
            SerialPort.objects.bulk_create(
                [SerialPort(device=self, name=template.name, notes=template.notes) for template in
                 self.device_definition.serial_port_templates.all()]
            )
            PowerPort.objects.bulk_create(
                [PowerPort(device=self, name=template.name, notes=template.notes) for template in
                 self.device_definition.power_port_templates.all()]
            )
            PowerOutlet.objects.bulk_create(
                [PowerOutlet(device=self, name=template.name, notes=template.notes) for template in
                 self.device_definition.power_outlet_templates.all()]
            )
            Interface.objects.bulk_create(
                [Interface(device=self, name=template.name, form_factor=template.form_factor,
                           mgmt_only=template.mgmt_only, notes=template.notes) for template in
                 self.device_definition.interface_templates.all()]
            )


    @property
    def display_name(self):
        if self.name:
            return self.name
        elif hasattr(self, 'device_definition'):
            return "{}".format(self.device_definition)
        return ""

    # @property
    # def primary_ip(self):
    #     if settings.PREFER_IPV4 and self.primary_ip4:
    #         return self.primary_ip4
    #     elif self.primary_ip6:
    #         return self.primary_ip6
    #     elif self.primary_ip4:
    #         return self.primary_ip4
    #     else:
    #         return None

    def get_status_css_class(self):
        return DEVICE_STATUS_CSS[self.status]


# Serial ports
#
class SerialPort(models.Model):
    """
    A physical serial port on a Device.
    """
    device = models.ForeignKey('Device', related_name='console_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    connected_to = models.OneToOneField('self', related_name='+',
                                        on_delete=models.SET_NULL,
                                        verbose_name='Connected serial port', blank=True, null=True)
    connection_status = models.NullBooleanField(choices=CONNECTION_STATUS_CHOICES,
                                                default=CONNECTION_STATUS_CONNECTED)

    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )

    class Meta:
        app_label = 'infrastructure'
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(SerialPort, self).save(*args, **kwargs)
        if self.connected_to and self.connected_to != self:
            self.connected_to.connected_to = self
            self.connected_to.connected_to.save()


# Power ports
#
class PowerPort(models.Model):
    """
    A physical power supply (intake) port within a Device. PowerPorts connect to PowerOutlets.
    """
    device = models.ForeignKey('Device', related_name='power_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    power_outlet = models.OneToOneField('PowerOutlet', related_name='connected_port',
                                        on_delete=models.SET_NULL,
                                        blank=True, null=True)
    connection_status = models.NullBooleanField(choices=CONNECTION_STATUS_CHOICES,
                                                default=CONNECTION_STATUS_CONNECTED)

    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )

    class Meta:
        app_label = 'infrastructure'
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name


# Power outlets
#
class PowerOutlet(models.Model):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    device = models.ForeignKey('Device', related_name='power_outlets', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )

    objects = PowerOutletManager()

    class Meta:
        app_label = 'infrastructure'
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name
