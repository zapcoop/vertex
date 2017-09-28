from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Q, ObjectDoesNotExist
from django.db.models.expressions import RawSQL
from django.urls import reverse

# from extras.models import CustomFieldModel, CustomField, CustomFieldValue, ImageAttachment
# from extras.rpc import RPC_CLIENTS
# from tenancy.models import Tenant
# from utilities.fields import ColorField, NullableCharField
# from utilities.managers import NaturalOrderByManager
# from utilities.models import CreatedUpdatedModel
# from utilities.utils import csv_format
from .constants import *
# from .fields import ASNField, MACAddressField

class DeviceType(models.Model):
    """
    A DeviceType represents a particular make (Manufacturer) and model of device. It specifies rack height and depth, as
    well as high-level functional role(s).

    Each DeviceType can have an arbitrary number of component templates assigned to it, which define console, power, and
    interface objects. For example, a Juniper EX4300-48T DeviceType would have:

      * 1 ConsolePortTemplate
      * 2 PowerPortTemplates
      * 48 InterfaceTemplates

    When a new Device of this type is created, the appropriate console, power, and interface objects (as defined by the
    DeviceType) are automatically created as well.
    """

    interface_ordering = models.PositiveSmallIntegerField(choices=IFACE_ORDERING_CHOICES,
                                                          default=IFACE_ORDERING_POSITION)
    is_console_server = models.BooleanField(default=False, verbose_name='Is a console server',
                                            help_text="This type of device has console server ports")
    is_pdu = models.BooleanField(default=False, verbose_name='Is a PDU',
                                 help_text="This type of device has power outlets")
    is_network_device = models.BooleanField(default=True, verbose_name='Is a network device',
                                            help_text="This type of device has network interfaces")
    subdevice_role = models.NullBooleanField(default=None, verbose_name='Parent/child status',
                                             choices=SUBDEVICE_ROLE_CHOICES,
                                             help_text="Parent devices house child devices in device bays. Select "
                                                       "\"None\" if this device type is neither a parent nor a child.")
    comments = models.TextField(blank=True)


    class Meta:
        ordering = ['manufacturer', 'model']
        unique_together = [
            ['manufacturer', 'model'],
            ['manufacturer', 'slug'],
        ]

    def __str__(self):
        return self.model

    def __init__(self, *args, **kwargs):
        super(DeviceType, self).__init__(*args, **kwargs)

        # Save a copy of u_height for validation in clean()
        self._original_u_height = self.u_height

    def get_absolute_url(self):
        return reverse('dcim:devicetype', args=[self.pk])

    def clean(self):

        # If editing an existing DeviceType to have a larger u_height, first validate that *all* instances of it have
        # room to expand within their racks. This validation will impose a very high performance penalty when there are
        # many instances to check, but increasing the u_height of a DeviceType should be a very rare occurrence.
        if self.pk is not None and self.u_height > self._original_u_height:
            for d in Device.objects.filter(device_type=self, position__isnull=False):
                face_required = None if self.is_full_depth else d.face
                u_available = d.rack.get_available_units(u_height=self.u_height,
                                                         rack_face=face_required,
                                                         exclude=[d.pk])
                if d.position not in u_available:
                    raise ValidationError({
                        'u_height': "Device {} in rack {} does not have sufficient space to accommodate a height of "
                                    "{}U".format(d, d.rack, self.u_height)
                    })

        if not self.is_console_server and self.cs_port_templates.count():
            raise ValidationError({
                'is_console_server': "Must delete all console server port templates associated with this device before "
                                     "declassifying it as a console server."
            })

        if not self.is_pdu and self.power_outlet_templates.count():
            raise ValidationError({
                'is_pdu': "Must delete all power outlet templates associated with this device before declassifying it "
                          "as a PDU."
            })

        if not self.is_network_device and self.interface_templates.filter(mgmt_only=False).count():
            raise ValidationError({
                'is_network_device': "Must delete all non-management-only interface templates associated with this "
                                     "device before declassifying it as a network device."
            })

        if self.subdevice_role != SUBDEVICE_ROLE_PARENT and self.device_bay_templates.count():
            raise ValidationError({
                'subdevice_role': "Must delete all device bay templates associated with this device before "
                                  "declassifying it as a parent device."
            })

        if self.u_height and self.subdevice_role == SUBDEVICE_ROLE_CHILD:
            raise ValidationError({
                'u_height': "Child device types must be 0U."
            })

    @property
    def full_name(self):
        return '{} {}'.format(self.manufacturer.name, self.model)

    @property
    def is_parent_device(self):
        return bool(self.subdevice_role)

    @property
    def is_child_device(self):
        return bool(self.subdevice_role is False)


class ConsolePortTemplate(models.Model):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='console_port_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

class ConsoleServerPortTemplate(models.Model):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='cs_port_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class PowerPortTemplate(models.Model):
    """
    A template for a PowerPort to be created for a new Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='power_port_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class PowerOutletTemplate(models.Model):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='power_outlet_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class InterfaceQuerySet(models.QuerySet):
    def order_naturally(self, method=IFACE_ORDERING_POSITION):
        """
        Naturally order interfaces by their type and numeric position. The sort method must be one of the defined
        IFACE_ORDERING_CHOICES (typically indicated by a parent Device's DeviceType).

        To order interfaces naturally, the `name` field is split into six distinct components: leading text (type),
        slot, subslot, position, channel, and virtual circuit:

            {type}{slot}/{subslot}/{position}/{subposition}:{channel}.{vc}

        Components absent from the interface name are ignored. For example, an interface named GigabitEthernet1/2/3
        would be parsed as follows:

            name = 'GigabitEthernet'
            slot =  1
            subslot = 2
            position = 3
            subposition = 0
            channel = None
            vc = 0

        The original `name` field is taken as a whole to serve as a fallback in the event interfaces do not match any of
        the prescribed fields.
        """
        sql_col = '{}.name'.format(self.model._meta.db_table)
        ordering = {
            IFACE_ORDERING_POSITION: (
                '_slot', '_subslot', '_position', '_subposition', '_channel', '_vc', '_type', '_id',
                'name',
            ),
            IFACE_ORDERING_NAME: (
                '_type', '_slot', '_subslot', '_position', '_subposition', '_channel', '_vc', '_id',
                'name',
            ),
        }[method]

        TYPE_RE = r"SUBSTRING({} FROM '^([^0-9]+)')"
        ID_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)([0-9]+)$') AS integer)"
        SLOT_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)([0-9]+)\/') AS integer)"
        SUBSLOT_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)(?:[0-9]+\/)([0-9]+)') AS integer)"
        POSITION_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)(?:[0-9]+\/){{2}}([0-9]+)') AS integer)"
        SUBPOSITION_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)(?:[0-9]+\/){{3}}([0-9]+)') AS integer)"
        CHANNEL_RE = r"COALESCE(CAST(SUBSTRING({} FROM ':([0-9]+)(\.[0-9]+)?$') AS integer), 0)"
        VC_RE = r"COALESCE(CAST(SUBSTRING({} FROM '\.([0-9]+)$') AS integer), 0)"

        fields = {
            '_type': RawSQL(TYPE_RE.format(sql_col), []),
            '_id': RawSQL(ID_RE.format(sql_col), []),
            '_slot': RawSQL(SLOT_RE.format(sql_col), []),
            '_subslot': RawSQL(SUBSLOT_RE.format(sql_col), []),
            '_position': RawSQL(POSITION_RE.format(sql_col), []),
            '_subposition': RawSQL(SUBPOSITION_RE.format(sql_col), []),
            '_channel': RawSQL(CHANNEL_RE.format(sql_col), []),
            '_vc': RawSQL(VC_RE.format(sql_col), []),
        }

        return self.annotate(**fields).order_by(*ordering)

    def connectable(self):
        """
        Return only physical interfaces which are capable of being connected to other interfaces (i.e. not virtual or
        wireless).
        """
        return self.exclude(form_factor__in=NONCONNECTABLE_IFACE_TYPES)


class InterfaceTemplate(models.Model):
    """
    A template for a physical data interface on a new Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='interface_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    form_factor = models.PositiveSmallIntegerField(choices=IFACE_FF_CHOICES,
                                                   default=IFACE_FF_10GE_SFP_PLUS)
    mgmt_only = models.BooleanField(default=False, verbose_name='Management only')

    objects = InterfaceQuerySet.as_manager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class DeviceBayTemplate(models.Model):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='device_bay_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


#
# Devices
#

class DeviceRole(models.Model):
    """
    Devices are organized by functional role; for example, "Core Switch" or "File Server". Each DeviceRole is assigned a
    color to be used when displaying rack elevations.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = ColorField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?role={}".format(reverse('dcim:device_list'), self.slug)


class Platform(models.Model):
    """
    Platform refers to the software or firmware running on a Device; for example, "Cisco IOS-XR" or "Juniper Junos".
    NetBox uses Platforms to determine how to interact with devices when pulling inventory data or other information by
    specifying an remote procedure call (RPC) client.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    napalm_driver = models.CharField(max_length=50, blank=True, verbose_name='NAPALM driver',
                                     help_text="The name of the NAPALM driver to use when interacting with devices.")
    rpc_client = models.CharField(max_length=30, choices=RPC_CLIENT_CHOICES, blank=True,
                                  verbose_name='Legacy RPC client')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?platform={}".format(reverse('dcim:device_list'), self.slug)


class DeviceManager(NaturalOrderByManager):
    def get_queryset(self):
        return self.natural_order_by('name')


class Device(CreatedUpdatedModel, CustomFieldModel):
    """
    A Device represents a piece of physical hardware mounted within a Rack. Each Device is assigned a DeviceType,
    DeviceRole, and (optionally) a Platform. Device names are not required, however if one is set it must be unique.

    Each Device must be assigned to a site, and optionally to a rack within that site. Associating a device with a
    particular rack face or unit is optional (for example, vertically mounted PDUs do not consume rack units).

    When a new Device is created, console/power/interface/device bay components are created along with it as dictated
    by the component templates assigned to its DeviceType. Components can also be added, modified, or deleted after the
    creation of a Device.
    """
    device_type = models.ForeignKey('inventory.DeviceType', related_name='instances',
                                    on_delete=models.PROTECT)
    device_role = models.ForeignKey('DeviceRole', related_name='devices', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, blank=True, null=True, related_name='devices',
                               on_delete=models.PROTECT)
    platform = models.ForeignKey('Platform', related_name='devices', blank=True, null=True,
                                 on_delete=models.SET_NULL)
    name = NullableCharField(max_length=64, blank=True, null=True, unique=True)
    serial = models.CharField(max_length=50, blank=True, verbose_name='Serial number')
    asset_tag = NullableCharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name='Asset tag',
        help_text='A unique tag used to identify this device'
    )
    site = models.ForeignKey('Site', related_name='devices', on_delete=models.PROTECT)
    rack = models.ForeignKey('Rack', related_name='devices', blank=True, null=True,
                             on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(
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

    csv_headers = [
        'name', 'device_role', 'tenant', 'manufacturer', 'model_name', 'platform', 'serial',
        'asset_tag', 'status',
        'site', 'rack_group', 'rack_name', 'position', 'face',
    ]

    class Meta:
        ordering = ['name']
        unique_together = ['rack', 'position', 'face']
        permissions = (
            ('napalm_read', 'Read-only access to devices via NAPALM'),
            ('napalm_write', 'Read/write access to devices via NAPALM'),
        )

    def __str__(self):
        return self.display_name or super(Device, self).__str__()

    def get_absolute_url(self):
        return reverse('dcim:device', args=[self.pk])

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
                if self.device_type.is_child_device and self.face is not None:
                    raise ValidationError({
                        'face': "Child device types cannot be assigned to a rack face. This is an attribute of the "
                                "parent device."
                    })
                if self.device_type.is_child_device and self.position:
                    raise ValidationError({
                        'position': "Child device types cannot be assigned to a rack position. This is an attribute of "
                                    "the parent device."
                    })

                # Validate rack space
                rack_face = self.face if not self.device_type.is_full_depth else None
                exclude_list = [self.pk] if self.pk else []
                try:
                    available_units = self.rack.get_available_units(
                        u_height=self.device_type.u_height, rack_face=rack_face,
                        exclude=exclude_list
                    )
                    if self.position and self.position not in available_units:
                        raise ValidationError({
                            'position': "U{} is already occupied or does not have sufficient space to accommodate a(n) "
                                        "{} ({}U).".format(self.position, self.device_type,
                                                           self.device_type.u_height)
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
                'primary_ip4': "The specified IP address ({}) is not assigned to this device.".format(
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
                'primary_ip6': "The specified IP address ({}) is not assigned to this device.".format(
                    self.primary_ip6),
            })

    def save(self, *args, **kwargs):

        is_new = not bool(self.pk)

        super(Device, self).save(*args, **kwargs)

        # If this is a new Device, instantiate all of the related components per the DeviceType definition
        if is_new:
            ConsolePort.objects.bulk_create(
                [ConsolePort(device=self, name=template.name) for template in
                 self.device_type.console_port_templates.all()]
            )
            ConsoleServerPort.objects.bulk_create(
                [ConsoleServerPort(device=self, name=template.name) for template in
                 self.device_type.cs_port_templates.all()]
            )
            PowerPort.objects.bulk_create(
                [PowerPort(device=self, name=template.name) for template in
                 self.device_type.power_port_templates.all()]
            )
            PowerOutlet.objects.bulk_create(
                [PowerOutlet(device=self, name=template.name) for template in
                 self.device_type.power_outlet_templates.all()]
            )
            Interface.objects.bulk_create(
                [Interface(device=self, name=template.name, form_factor=template.form_factor,
                           mgmt_only=template.mgmt_only) for template in
                 self.device_type.interface_templates.all()]
            )
            DeviceBay.objects.bulk_create(
                [DeviceBay(device=self, name=template.name) for template in
                 self.device_type.device_bay_templates.all()]
            )

        # Update Site and Rack assignment for any child Devices
        Device.objects.filter(parent_bay__device=self).update(site=self.site, rack=self.rack)

    def to_csv(self):
        return csv_format([
            self.name or '',
            self.device_role.name,
            self.tenant.name if self.tenant else None,
            self.device_type.manufacturer.name,
            self.device_type.model,
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
        elif hasattr(self, 'device_type'):
            return "{}".format(self.device_type)
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
        Return the appropriate RPC (e.g. NETCONF, ssh, etc.) client for this device's platform, if one is defined.
        """
        if not self.platform:
            return None
        return RPC_CLIENTS.get(self.platform.rpc_client)


#
# Console ports
#

@python_2_unicode_compatible
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
        ])


#
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
            'name_as_integer': "CAST(substring(dcim_consoleserverport.name FROM '[0-9]+$') AS INTEGER)",
        }).order_by('device', 'name_as_integer')


@python_2_unicode_compatible
class ConsoleServerPort(models.Model):
    """
    A physical port within a Device (typically a designated console server) which provides access to ConsolePorts.
    """
    device = models.ForeignKey('Device', related_name='cs_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = ConsoleServerPortManager()

    class Meta:
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name


#
# Power ports
#

@python_2_unicode_compatible
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
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    # Used for connections export
    def to_csv(self):
        return csv_format([
            self.power_outlet.device.identifier if self.power_outlet else None,
            self.power_outlet.name if self.power_outlet else None,
            self.device.identifier,
            self.name,
            self.get_connection_status_display(),
        ])


#
# Power outlets
#

class PowerOutletManager(models.Manager):
    def get_queryset(self):
        return super(PowerOutletManager, self).get_queryset().extra(select={
            'name_padded': "CONCAT(SUBSTRING(dcim_poweroutlet.name FROM '^[^0-9]+'), "
                           "LPAD(SUBSTRING(dcim_poweroutlet.name FROM '[0-9\/]+$'), 8, '0'))",
        }).order_by('device', 'name_padded')


@python_2_unicode_compatible
class PowerOutlet(models.Model):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    device = models.ForeignKey('Device', related_name='power_outlets', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = PowerOutletManager()

    class Meta:
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name


#
# Interfaces
#

@python_2_unicode_compatible
class Interface(models.Model):
    """
    A physical data interface within a Device. An Interface can connect to exactly one other Interface via the creation
    of an InterfaceConnection.
    """
    device = models.ForeignKey('Device', related_name='interfaces', on_delete=models.CASCADE)
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
    mac_address = MACAddressField(null=True, blank=True, verbose_name='MAC Address')
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
                'form_factor': "Virtual and wireless interfaces cannot be connected to another interface or circuit. "
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
                'form_factor': "Cannot change interface form factor; it has LAG members ({}).".format(
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
        try:
            return bool(self.circuit_termination)
        except ObjectDoesNotExist:
            pass
        return bool(self.connection)

    @property
    def connection(self):
        try:
            return self.connected_as_a
        except ObjectDoesNotExist:
            pass
        try:
            return self.connected_as_b
        except ObjectDoesNotExist:
            pass
        return None

    @property
    def connected_interface(self):
        try:
            if self.connected_as_a:
                return self.connected_as_a.interface_b
        except ObjectDoesNotExist:
            pass
        try:
            if self.connected_as_b:
                return self.connected_as_b.interface_a
        except ObjectDoesNotExist:
            pass
        return None


class InterfaceConnection(models.Model):
    """
    An InterfaceConnection represents a symmetrical, one-to-one connection between two Interfaces. There is no
    significant difference between the interface_a and interface_b fields.
    """
    interface_a = models.OneToOneField('Interface', related_name='connected_as_a',
                                       on_delete=models.CASCADE)
    interface_b = models.OneToOneField('Interface', related_name='connected_as_b',
                                       on_delete=models.CASCADE)
    connection_status = models.BooleanField(choices=CONNECTION_STATUS_CHOICES,
                                            default=CONNECTION_STATUS_CONNECTED,
                                            verbose_name='Status')

    csv_headers = ['device_a', 'interface_a', 'device_b', 'interface_b', 'connection_status']

    def clean(self):
        try:
            if self.interface_a == self.interface_b:
                raise ValidationError({
                    'interface_b': "Cannot connect an interface to itself."
                })
        except ObjectDoesNotExist:
            pass

    # Used for connections export
    def to_csv(self):
        return csv_format([
            self.interface_a.device.identifier,
            self.interface_a.name,
            self.interface_b.device.identifier,
            self.interface_b.name,
            self.get_connection_status_display(),
        ])


#
# Device bays
#

@python_2_unicode_compatible
class DeviceBay(models.Model):
    """
    An empty space within a Device which can house a child device
    """
    device = models.ForeignKey('Device', related_name='device_bays', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Name')
    installed_device = models.OneToOneField('Device', related_name='parent_bay',
                                            on_delete=models.SET_NULL, blank=True,
                                            null=True)

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return '{} - {}'.format(self.device.name, self.name)

    def clean(self):

        # Validate that the parent Device can have DeviceBays
        if not self.device.device_type.is_parent_device:
            raise ValidationError("This type of device ({}) does not support device bays.".format(
                self.device.device_type
            ))

        # Cannot install a device into itself, obviously
        if self.device == self.installed_device:
            raise ValidationError("Cannot install a device into itself.")


#
# Inventory items
#

@python_2_unicode_compatible
class InventoryItem(models.Model):
    """
    An InventoryItem represents a serialized piece of hardware within a Device, such as a line card or power supply.
    InventoryItems are used only for inventory purposes.
    """
    device = models.ForeignKey('Device', related_name='inventory_items', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='child_items', blank=True, null=True,
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Name')
    manufacturer = models.ForeignKey(
        'Manufacturer', models.PROTECT, related_name='inventory_items', blank=True, null=True
    )
    part_id = models.CharField(max_length=50, verbose_name='Part ID', blank=True)
    serial = models.CharField(max_length=50, verbose_name='Serial number', blank=True)
    asset_tag = NullableCharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name='Asset tag',
        help_text='A unique tag used to identify this item'
    )
    discovered = models.BooleanField(default=False, verbose_name='Discovered')
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['device__id', 'parent__id', 'name']
        unique_together = ['device', 'parent', 'name']

    def __str__(self):
        return self.name
