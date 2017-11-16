from django.core.exceptions import ValidationError
from django.db import models

from infrastructure.constants import *
from vertex.models import AbstractDatedModel


class DeviceDefinition(AbstractDatedModel):
    """
    A DeviceDefinition specifies high-level functional role(s) of a specific item.

    Each DeviceDefinition can have an arbitrary number of component templates assigned to it, which define power, and
    interface objects. For example, a Juniper EX4300-48T DeviceType would have:

      * 1 ConsolePortTemplate
      * 2 PowerPortTemplates
      * 48 InterfaceTemplates

    When a new Device of this type is created, the appropriate console, power, and interface objects (as defined by the
    DeviceType) are automatically created as well.
    """
    item = models.OneToOneField('inventory.Item')

    interface_ordering = models.PositiveSmallIntegerField(choices=IFACE_ORDERING_CHOICES,
                                                          default=IFACE_ORDERING_POSITION)
    has_serial_ports = models.BooleanField(default=False, verbose_name='Has serial port(s)',
                                           help_text="This type of device has serial console ports")
    has_power_outlets = models.BooleanField(default=False, verbose_name='Has power outlet(s)',
                                            help_text="This type of device has power outlets")
    has_network_interfaces = models.BooleanField(default=True,
                                                 verbose_name='Is a network enabled device',
                                                 help_text="This type of device has network interfaces")
    subdevice_role = models.NullBooleanField(default=None, verbose_name='Parent/child status',
                                             choices=SUBDEVICE_ROLE_CHOICES,
                                             help_text="Parent devices house child devices in device bays. Select "
                                                       "\"None\" if this device type is neither a parent nor a child.")
    notes = models.TextField(verbose_name=_('Notes'), blank=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.item)

    def __init__(self, *args, **kwargs):
        super(DeviceDefinition, self).__init__(*args, **kwargs)

    def clean(self):

        if not self.has_serial_ports and self.serial_port_templates.count():
            raise ValidationError({
                'has_serial_ports': "Must delete all console server port templates associated with this device before "
                                    "declassifying it as a console server."
            })

        if not self.has_power_outlets and self.power_outlet_templates.count():
            raise ValidationError({
                'has_power_outlets': "Must delete all power outlet templates associated with this device before declassifying it "
                                     "as a PDU."
            })

        if not self.has_network_interfaces and self.interface_templates.filter(
                mgmt_only=False).count():
            raise ValidationError({
                'has_network_interfaces': "Must delete all non-management-only interface templates associated with this "
                                          "device before declassifying it as a network device."
            })

        if self.subdevice_role != SUBDEVICE_ROLE_PARENT and self.device_bay_templates.count():
            raise ValidationError({
                'subdevice_role': "Must delete all device bay templates associated with this device before "
                                  "declassifying it as a parent device."
            })

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
    device_type = models.ForeignKey('inventory.DeviceDefinition',
                                    related_name='console_port_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


class SerialPortTemplate(models.Model):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    device_type = models.ForeignKey('inventory.DeviceDefinition', related_name='cs_port_templates',
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
    device_type = models.ForeignKey('inventory.DeviceDefinition',
                                    related_name='power_port_templates',
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
    device_type = models.ForeignKey('inventory.DeviceDefinition',
                                    related_name='power_outlet_templates',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name
