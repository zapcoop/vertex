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






#
# Devices
#


#
# Interfaces
#

#
# Device bays
#


#
# Stockroom items
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
