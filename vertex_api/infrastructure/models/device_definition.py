# Heavily inspired from https://github.com/digitalocean/netbox/

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from infrastructure.constants import *
from infrastructure.querysets import InterfaceQuerySet
from vertex.models import AbstractDatedModel


class DeviceDefinition(AbstractDatedModel):
    """
    A DeviceDefinition specifies high-level functional role(s) of a specific item.

    Each DeviceDefinition can have an arbitrary number of component templates assigned to it, which
    define power, and interface objects. For example, a Juniper EX4300-48T DeviceType would have:

      * 1 ConsolePortTemplate
      * 2 PowerPortTemplates
      * 48 InterfaceTemplates

    When a new Device of this type is created, the appropriate console, power, and interface objects
    (as defined by the DeviceDefinition) are automatically created as well.
    """
    item = models.OneToOneField(
        'inventory.Item'
    )

    interface_ordering = models.PositiveSmallIntegerField(
        choices=IFACE_ORDERING_CHOICES,
        default=IFACE_ORDERING_POSITION
    )
    has_serial_ports = models.BooleanField(
        default=False,
        verbose_name='Has serial port(s)',
        help_text="This type of device has serial console ports used "
                  "to control other serial devices"
    )
    has_power_outlets = models.BooleanField(
        default=False,
        verbose_name='Has power outlet(s)',
        help_text="This type of device has power outlets"
    )
    has_network_interfaces = models.BooleanField(
        default=True,
        verbose_name='Is a network enabled device',
        help_text="This type of device has one or more network interfaces that are not dedicated "
                  "to management"
    )

    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )

    class Meta:
        app_label = 'infrastructure'

    def __str__(self):
        return str(self.item)

    def __init__(self, *args, **kwargs):
        super(DeviceDefinition, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.has_power_outlets and self.power_outlet_templates.count():
            raise ValidationError({
                'has_power_outlets': "You must remove all power outlet templates associated with "
                                     "this device before declassifying it as a power distribution"
                                     "equipment."
            })

        if not self.has_network_interfaces and self.interface_templates.filter(
                mgmt_only=False).count():
            raise ValidationError({
                'has_network_interfaces': "You must remove all interface templates that are not "
                                          "dedicated to management associated with this device "
                                          "before declassifying it as a network device."
            })


class AbstractDeviceDefinitionTemplateModel(AbstractDatedModel):
    """
    An abstract class for template models to be created for a new Device.
    """
    name = models.CharField(max_length=64)
    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['device_definition', 'name']
        unique_together = ['device_definition', 'name']
        app_label = 'infrastructure'


class SerialPortTemplate(AbstractDeviceDefinitionTemplateModel):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    device_definition = models.ForeignKey(
        'infrastructure.DeviceDefinition',
        related_name='serial_port_templates',
        on_delete=models.CASCADE
    )


class PowerPortTemplate(AbstractDeviceDefinitionTemplateModel):
    """
    A template for a PowerPort to be created for a new Device.
    """
    device_definition = models.ForeignKey(
        'infrastructure.DeviceDefinition',
        related_name='power_port_templates',
        on_delete=models.CASCADE
    )


class PowerOutletTemplate(AbstractDeviceDefinitionTemplateModel):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    device_definition = models.ForeignKey(
        'infrastructure.DeviceDefinition',
        related_name='power_outlet_templates',
        on_delete=models.CASCADE
    )


class InterfaceTemplate(AbstractDeviceDefinitionTemplateModel):
    """
    A template for a physical data interface on a new Device.
    """
    device_definition = models.ForeignKey(
        'infrastructure.DeviceDefinition',
        related_name='interface_templates',
        on_delete=models.CASCADE
    )

    form_factor = models.PositiveSmallIntegerField(
        choices=IFACE_FF_CHOICES,
        default=IFACE_FF_10GE_SFP_PLUS
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='Management only'
    )

    objects = InterfaceQuerySet.as_manager()

    def __str__(self):
        return self.name
