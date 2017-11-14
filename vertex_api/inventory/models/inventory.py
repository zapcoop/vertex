from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from vertex.models import AbstractDatedModel

class ItemParts(AbstractDatedModel):
    item = models.ForeignKey('inventory.Item')
    part = models.ForeignKey('inventory.Part', related_name="used_by")
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))



class Item(AbstractDatedModel):
    manufacturer = models.ForeignKey('contacts.Manufacturer', related_name='item_templates',
                                     on_delete=models.PROTECT)
    model = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, editable=False)
    part_number = models.CharField(max_length=50, blank=True,
                                   help_text=_("Discrete part number (optional)"))



    description = models.CharField(verbose_name=_('Description'), max_length=64, blank=True)

    notes = models.TextField(verbose_name=_('Notes'), null=True, blank=True)

    built_to_order = models.BooleanField(default=False)
    parts = models.ManyToManyField('inventory.Part', through=ItemParts, blank=True,
                                      verbose_name=_('Requires'))

    suppliers = models.ManyToManyField('contacts.HardwareSupplier', blank=True,
                                       verbose_name=_('Suppliers'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.manufacturer.slug + "-" + slugify(self.model))
        super(Item, self).save(*args,**kwargs)

    def __str__(self):
        return self.model

    class Meta:
        ordering = ['manufacturer', 'model']
        unique_together = (
            ('manufacturer', 'model')
        )
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        app_label = 'inventory'



class PartManager(models.Manager):
    def get_queryset(self):
        return super(PartManager, self).get_queryset().filter(built_to_order=False)


class Part(Item):
    class Meta:
        proxy = True

    objects = PartManager()


class Stockroom(models.Model):
    name = models.CharField(max_length=32, verbose_name=_('Name'))
    location = models.ForeignKey('places.Place', verbose_name=_('Location'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Stockroom')
        verbose_name_plural = _('Stockrooms')
        app_label = 'inventory'


class InventoryCheckPoint(models.Model):
    stockroom = models.ForeignKey(Stockroom, verbose_name=_('Stockroom'))
    datetime = models.DateTimeField(default=timezone.now, verbose_name=_('Date & time'))
    supplies = models.ManyToManyField(Item, blank=True, through='InventoryCPQty',
                                      verbose_name=_('Supplies'))

    class Meta:
        app_label = 'inventory'


class InventoryCPQty(models.Model):
    supply = models.ForeignKey(Item, verbose_name=_('Supply'))
    check_point = models.ForeignKey(InventoryCheckPoint, verbose_name=_('Check point'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))

    class Meta:
        app_label = 'inventory'


class InventoryTransaction(models.Model):
    stockroom = models.ForeignKey(Stockroom, related_name='transactions',
                                  verbose_name=_('Stockroom'))
    supply = models.ForeignKey(Item, verbose_name=_('Supply'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    date = models.DateField(default=timezone.now, verbose_name=_('Date'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notes'))

    class Meta:
        verbose_name = _('Stockroom transaction')
        verbose_name_plural = _('Stockroom transactions')
        ordering = ['-date', '-id']
        app_label = 'inventory'

    def __str__(self):
        return "%s: '%s' qty=%s @ %s" % (self.stockroom, self.supply, self.quantity, self.date)
