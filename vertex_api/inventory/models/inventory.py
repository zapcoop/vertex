import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from vertex.models import AbstractDatedModel


class ItemTemplate(AbstractDatedModel):
    manufacturer = models.ForeignKey('contacts.Manufacturer', related_name='item_templates',
                                     on_delete=models.PROTECT)
    model = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    part_number = models.CharField(max_length=50, blank=True,
                                   help_text="Discrete part number (optional)")

    description = models.CharField(verbose_name=_('Description'), max_length=64, blank=True)

    notes = models.TextField(verbose_name=_('Notes'), null=True, blank=True)
    supplies = models.ManyToManyField('self', blank=True, verbose_name=_('Supplies'))
    suppliers = models.ManyToManyField('contacts.HardwareSupplier', blank=True,
                                       verbose_name=_('Suppliers'))

    def __str__(self):
        return self.model

    class Meta:
        ordering = ['manufacturer', 'model']
        unique_together = (
            ('manufacturer', 'model')
        )
        verbose_name = _('Item template')
        verbose_name_plural = _('Item templates')
        app_label = 'inventory'


class Log(models.Model):
    timedate = models.DateTimeField(auto_now_add=True, verbose_name=_('Date & time'))
    action = models.CharField(max_length=32, verbose_name=_('Action'))
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return '%s, %s - %s' % (self.timedate, self.action, self.content_object)

    class Meta:
        app_label = 'inventory'


class Inventory(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'))
    location = models.ForeignKey('places.Place', verbose_name=_('Location'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Inventory')
        verbose_name_plural = _('Inventories')
        app_label = 'inventory'


class InventoryCheckPoint(models.Model):
    inventory = models.ForeignKey(Inventory, verbose_name=_('Inventory'))
    datetime = models.DateTimeField(default=timezone.now, verbose_name=_('Date & time'))
    supplies = models.ManyToManyField(ItemTemplate, blank=True, through='InventoryCPQty',
                                      verbose_name=_('Supplies'))

    class Meta:
        app_label = 'inventory'


class InventoryCPQty(models.Model):
    supply = models.ForeignKey(ItemTemplate, verbose_name=_('Supply'))
    check_point = models.ForeignKey(InventoryCheckPoint, verbose_name=_('Check point'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))

    class Meta:
        app_label = 'inventory'


class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, related_name='transactions',
                                  verbose_name=_('Inventory'))
    supply = models.ForeignKey(ItemTemplate, verbose_name=_('Supply'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    date = models.DateField(default=timezone.now, verbose_name=_('Date'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notes'))

    class Meta:
        verbose_name = _('Inventory transaction')
        verbose_name_plural = _('Inventory transactions')
        ordering = ['-date', '-id']
        app_label = 'inventory'

    def __str__(self):
        return "%s: '%s' qty=%s @ %s" % (self.inventory, self.supply, self.quantity, self.date)

#
# register(ItemTemplate, _('Templates'), ['description', 'brand', 'model', 'part_number', 'notes'])
# register(Location, _('Locations'),
#          ['name', 'address_line1', 'address_line2', 'address_line3', 'address_line4',
#           'phone_number1', 'phone_number2'])
# register(Inventory, _('Inventory'), ['name', 'location__name'])
# register(Supplier, _('Supplier'),
#          ['name', 'address_line1', 'address_line2', 'address_line3', 'address_line4',
#           'phone_number1', 'phone_number2', 'notes'])
