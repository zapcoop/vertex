from django.db import models
from django.utils.translation import ugettext_lazy as _


class PurchaseRequestStatus(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=32)

    class Meta:
        verbose_name = _('Purchase request status')
        verbose_name_plural = _('Purchase request status')
        app_label = 'inventory'

    def __str__(self):
        return self.name


class PurchaseRequest(models.Model):
    user_id = models.CharField(max_length=32, null=True, blank=True,
                               verbose_name=_('User defined ID (optional)'))
    issue_date = models.DateField(auto_now_add=True, verbose_name=_('Issue date'))
    required_date = models.DateField(null=True, blank=True, verbose_name=_('Date required'))
    budget = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Budget'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    status = models.ForeignKey(PurchaseRequestStatus, null=True, blank=True,
                               verbose_name=_('Status'))
    originator = models.CharField(max_length=64, null=True, blank=True,
                                  verbose_name=_('Originator'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notes'))

    class Meta:
        verbose_name = _('Purchase request')
        verbose_name_plural = _('Purchase requests')
        app_label = 'inventory'

    def __str__(self):
        return '#%s (%s)' % (self.user_id if self.user_id else self.id, self.issue_date)

    class Meta:
        verbose_name = _('Purchase request')
        verbose_name_plural = _('Purchase requests')
        app_label = 'inventory'


class PurchaseRequestItem(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, related_name='items',
                                         verbose_name=_('Purchase request'))
    base_item = models.ForeignKey('inventory.BaseItem', verbose_name=_('Asset template'))
    qty = models.PositiveIntegerField(verbose_name=_('Quantity'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notes'))

    def __str__(self):
        return str(self.base_item)

    class Meta:
        verbose_name = _('Purchase request item')
        verbose_name_plural = _('Purchase request items')
        app_label = 'inventory'


class PurchaseOrderStatus(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Purchase order status')
        verbose_name_plural = _('Purchase order status')
        app_label = 'inventory'


class PurchaseOrder(models.Model):
    user_id = models.CharField(max_length=32, null=True, blank=True,
                               verbose_name=_('User defined ID'))
    purchase_request = models.ForeignKey(PurchaseRequest, null=True, blank=True,
                                         verbose_name=_('Purchase request'))
    supplier = models.ForeignKey('contacts.HardwareSupplier', related_name='purchase_orders',
                                 verbose_name=_('Supplier'))
    issue_date = models.DateField(auto_now_add=True, verbose_name=_('Issue date'))
    required_date = models.DateField(null=True, blank=True, verbose_name=_('Date required'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notes'))
    status = models.ForeignKey(PurchaseOrderStatus, null=True, blank=True, verbose_name=_('Status'))

    def __str__(self):
        return '#%s (%s)' % (self.user_id if self.user_id else self.id, self.issue_date)

    class Meta:
        verbose_name = _('Purchase order')
        verbose_name_plural = _('Purchase orders')
        app_label = 'inventory'


class PurchaseOrderItemStatus(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Purchase order item status')
        verbose_name_plural = _('Purchase order item status')
        app_label = 'inventory'


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items',
                                       verbose_name=_('Purchase order'))
    base_item = models.ForeignKey('inventory.BaseItem', verbose_name=_('Asset template'))
    agreed_price = models.PositiveIntegerField(null=True, blank=True,
                                               verbose_name=_('Agreed price'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    status = models.ForeignKey(PurchaseOrderItemStatus, null=True, blank=True,
                               verbose_name=_('Status'))
    qty = models.PositiveIntegerField(verbose_name=_('Quantity'))
    received_qty = models.PositiveIntegerField(default=0, null=True, blank=True,
                                               verbose_name=_('received'))

    def __str__(self):
        return str(self.base_item)

    class Meta:
        verbose_name = _('Purchase order item')
        verbose_name_plural = _('Purchase order items')
        app_label = 'inventory'

# register(PurchaseRequestStatus, _('Purchase request status'), ['name'])
# register(PurchaseRequest, _('Purchase request'), ['user_id', 'id', 'budget', 'required_date', 'status__name', 'originator'])
# register(PurchaseRequestItem, _('Purchase request item'), ['item_template__description', 'qty', 'notes'])
# register(PurchaseOrderStatus, _('Purchase order status'), ['name'])
# register(PurchaseOrderItemStatus, _('Purchase order item status'), ['name'])
# register(PurchaseOrder, _('Purchase order'), ['user_id', 'id', 'required_date', 'status__name', 'supplier__name', 'notes'])
# register(PurchaseOrderItem, _('Purchase order item'), ['item_template__description', 'qty'])
