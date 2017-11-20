# Heavily inspired from https://github.com/digitalocean/netbox/

from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from infrastructure.constants import *
from vertex.managers import NaturalOrderByManager
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
    slug = models.SlugField(
        unique=True
    )
    netmiko_type = models.CharField(
        max_length=50,
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


class DeviceManager(NaturalOrderByManager):
    def get_queryset(self):
        return self.natural_order_by('name')


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
        on_delete=models.PROTECT
    )
    device_role = models.ForeignKey(
        'infrastructure.DeviceRole',
        related_name='devices',
        on_delete=models.PROTECT
    )
    asset = models.ForeignKey(
        'inventory.assets',
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

    site = models.ForeignKey('Site', related_name='devices', on_delete=models.PROTECT)
    room = models.ForeignKey('Rack', related_name='devices', blank=True, null=True,
                             on_delete=models.PROTECT)
    wall = models.PositiveSmallIntegerField(
        blank=True, null=True, validators=[MinValueValidator(1)], verbose_name='Position (U)',
        help_text='The lowest-numbered unit occupied by the device'
    )
    face = models.PositiveSmallIntegerField(blank=True, null=True, choices=RACK_FACE_CHOICES,
                                            verbose_name='Rack face')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE,
                                              verbose_name='Status')
    primary_ip4 = models.OneToOneField(
        'ipam.IPAddress', related_name='primary_ip4_for', on_delete=models.SET_NULL, blank=True,
        null=True,
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        'ipam.IPAddress', related_name='primary_ip6_for', on_delete=models.SET_NULL, blank=True,
        null=True,
        verbose_name='Primary IPv6'
    )
    comments = models.TextField(blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type',
                                          object_id_field='obj_id')
    images = GenericRelation(ImageAttachment)

    objects = DeviceManager()

    class Meta:
        app_label = 'infrastructure'
        ordering = ['name']
        unique_together = ['rack', 'position', 'face']
        permissions = (
            ('napalm_read', 'Read-only access to devices via NAPALM'),
            ('napalm_write', 'Read/write access to devices via NAPALM'),
        )

    def __str__(self):
        return self.display_name or super(Device, self).__str__()

    def clean(self):
        # Validate site/rack combination
        if self.rack and self.site != self.rack.site:
            raise ValidationError({
                'rack': "Rack {} does not belong to site {}.".format(self.rack, self.site),
            })

        if self.rack is None:
            if self.face is not None:
                raise ValidationError({
                    'face': "Cannot select a rack face without assigning a rack.",
                })
            if self.position:
                raise ValidationError({
                    'face': "Cannot select a rack position without assigning a rack.",
                })

        # Validate position/face combination
        if self.position and self.face is None:
            raise ValidationError({
                'face': "Must specify rack face when defining rack position.",
            })

        if self.rack:

            try:
                # Child devices cannot be assigned to a rack face/unit
                if self.device_definition.is_child_device and self.face is not None:
                    raise ValidationError({
                        'face': "Child device types cannot be assigned to a rack face. This is an "
                                "attribute of the "
                                "parent device."
                    })
                if self.device_definition.is_child_device and self.position:
                    raise ValidationError({
                        'position': "Child device types cannot be assigned to a rack position. "
                                    "This is an attribute of "
                                    "the parent device."
                    })

                # Validate rack space
                rack_face = self.face if not self.device_definition.is_full_depth else None
                exclude_list = [self.pk] if self.pk else []
                try:
                    available_units = self.rack.get_available_units(
                        u_height=self.device_definition.u_height, rack_face=rack_face,
                        exclude=exclude_list
                    )
                    if self.position and self.position not in available_units:
                        raise ValidationError({
                            'position': "U{} is already occupied or does not have sufficient "
                                        "space to accommodate a(n) "
                                        "{} ({}U).".format(self.position, self.device_definition,
                                                           self.device_definition.u_height)
                        })
                except Rack.DoesNotExist:
                    pass

            except DeviceType.DoesNotExist:
                pass

        # Validate primary IPv4 address
        if self.primary_ip4 and (
                        self.primary_ip4.interface is None or
                        self.primary_ip4.interface.device != self
        ) and (
                        self.primary_ip4.nat_inside.interface is None or
                        self.primary_ip4.nat_inside.interface.device != self
        ):
            raise ValidationError({
                'primary_ip4': "The specified IP address ({}) is not assigned to this "
                               "device.".format(
                    self.primary_ip4),
            })

        # Validate primary IPv6 address
        if self.primary_ip6 and (
                        self.primary_ip6.interface is None or
                        self.primary_ip6.interface.device != self
        ) and (
                        self.primary_ip6.nat_inside.interface is None or
                        self.primary_ip6.nat_inside.interface.device != self
        ):
            raise ValidationError({
                'primary_ip6': "The specified IP address ({}) is not assigned to this "
                               "device.".format(
                    self.primary_ip6),
            })

    def save(self, *args, **kwargs):
        is_new = not bool(self.pk)

        super(Device, self).save(*args, **kwargs)

        # If this is a new Device, instantiate all of the related components per the DeviceType
        # definition
        if is_new:
            ConsolePort.objects.bulk_create(
                [ConsolePort(device=self, name=template.name) for template in
                 self.device_definition.console_port_templates.all()]
            )
            ConsoleServerPort.objects.bulk_create(
                [ConsoleServerPort(device=self, name=template.name) for template in
                 self.device_definition.cs_port_templates.all()]
            )
            PowerPort.objects.bulk_create(
                [PowerPort(device=self, name=template.name) for template in
                 self.device_definition.power_port_templates.all()]
            )
            PowerOutlet.objects.bulk_create(
                [PowerOutlet(device=self, name=template.name) for template in
                 self.device_definition.power_outlet_templates.all()]
            )
            Interface.objects.bulk_create(
                [Interface(device=self, name=template.name, form_factor=template.form_factor,
                           mgmt_only=template.mgmt_only) for template in
                 self.device_definition.interface_templates.all()]
            )
            DeviceBay.objects.bulk_create(
                [DeviceBay(device=self, name=template.name) for template in
                 self.device_definition.device_bay_templates.all()]
            )

        # Update Site and Rack assignment for any child Devices
        Device.objects.filter(parent_bay__device=self).update(site=self.site, rack=self.rack)

    def to_csv(self):
        return csv_format([
            self.name or '',
            self.device_role.name,
            self.tenant.name if self.tenant else None,
            self.device_definition.manufacturer.name,
            self.device_definition.model,
            self.platform.name if self.platform else None,
            self.serial,
            self.asset_tag,
            self.get_status_display(),
            self.site.name,
            self.rack.group.name if self.rack and self.rack.group else None,
            self.rack.name if self.rack else None,
            self.position,
            self.get_face_display(),
        ])

    @property
    def display_name(self):
        if self.name:
            return self.name
        elif hasattr(self, 'device_definition'):
            return "{}".format(self.device_definition)
        return ""

    @property
    def identifier(self):
        """
        Return the device name if set; otherwise return the Device's primary key as {pk}
        """
        if self.name is not None:
            return self.name
        return '{{{}}}'.format(self.pk)

    @property
    def primary_ip(self):
        if settings.PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    def get_children(self):
        """
        Return the set of child Devices installed in DeviceBays within this Device.
        """
        return Device.objects.filter(parent_bay__device=self.pk)

    def get_status_class(self):
        return DEVICE_STATUS_CLASSES[self.status]

    def get_rpc_client(self):
        """
        Return the appropriate RPC (e.g. NETCONF, ssh, etc.) client for this device's platform,
        if one is defined.
        """
        if not self.platform:
            return None
        return RPC_CLIENTS.get(self.platform.rpc_client)  #


# Console ports
#


class ConsolePort(models.Model):
    """
    A physical console port within a Device. ConsolePorts connect to ConsoleServerPorts.
    """
    device = models.ForeignKey('Device', related_name='console_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    cs_port = models.OneToOneField('ConsoleServerPort', related_name='connected_console',
                                   on_delete=models.SET_NULL,
                                   verbose_name='Console server port', blank=True, null=True)
    connection_status = models.NullBooleanField(choices=CONNECTION_STATUS_CHOICES,
                                                default=CONNECTION_STATUS_CONNECTED)

    csv_headers = ['console_server', 'cs_port', 'device', 'console_port', 'connection_status']

    class Meta:
        app_label = 'infrastructure'
        ordering = ['device', 'name']
        unique_together = ['device', 'name']


def __str__(self):
    return self.name


# Used for connections export
def to_csv(self):
    return csv_format([
        self.cs_port.device.identifier if self.cs_port else None,
        self.cs_port.name if self.cs_port else None,
        self.device.identifier,
        self.name,
        self.get_connection_status_display(),
    ])  #


# Console server ports
#

class ConsoleServerPortManager(models.Manager):
    def get_queryset(self):
        """
        Include the trailing numeric portion of each port name to allow for proper ordering.
        For example:
            Port 1, Port 2, Port 3 ... Port 9, Port 10, Port 11 ...
        Instead of:
            Port 1, Port 10, Port 11 ... Port 19, Port 2, Port 20 ...
        """
        return super(ConsoleServerPortManager, self).get_queryset().extra(select={
            'name_as_integer': "CAST(substring(dcim_consoleserverport.name FROM '[0-9]+$') AS "
                               "INTEGER)",
        }).order_by('device', 'name_as_integer')


class ConsoleServerPort(models.Model):
    """
    A physical port within a Device (typically a designated console server) which provides access
    to ConsolePorts.
    """
    device = models.ForeignKey('Device', related_name='cs_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = ConsoleServerPortManager()

    class Meta:
        app_label = 'infrastructure'
        unique_together = ['device', 'name']


def __str__(self):
    return self.name  #


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

    csv_headers = ['pdu', 'power_outlet', 'device', 'power_port', 'connection_status']

    class Meta:
        app_label = 'infrastructure'
        ordering = ['device', 'name']
        unique_together = ['device', 'name']


def __str__(self):
    return self.name  #


# Power outlets
#

class PowerOutletManager(models.Manager):
    def get_queryset(self):
        return super(PowerOutletManager, self).get_queryset().extra(select={
            'name_padded': "CONCAT(SUBSTRING(dcim_poweroutlet.name FROM '^[^0-9]+'), "
                           "LPAD(SUBSTRING(dcim_poweroutlet.name FROM '[0-9\/]+$'), 8, '0'))",
        }).order_by('device', 'name_padded')


class PowerOutlet(models.Model):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    device = models.ForeignKey('Device', related_name='power_outlets', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = PowerOutletManager()

    class Meta:
        app_label = 'infrastructure'
        unique_together = ['device', 'name']


def __str__(self):
    return self.name
