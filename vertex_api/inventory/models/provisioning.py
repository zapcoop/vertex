from django.db import models
from django.utils.translation import ugettext_lazy as _

from inventory.constants import PO_STATUS_CHOICES, PR_STATUS_CHOICES


class PurchaseRequest(models.Model):
    parent = models.ForeignKey(
        'self',
        related_name='children_pr_set',
        null=True,
        editable=False
    )

    user_id = models.CharField(
        max_length=32,
        blank=True,
        verbose_name=_('User defined ID (optional)')
    )
    issue_date = models.DateField(
        auto_now_add=True,
        verbose_name=_('Issue date')
    )
    required_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date required')
    )
    supplier_contact = models.ForeignKey(
        'contacts.EmailAddress',
        limit_choices_to={'organization__groups': 3},
        blank=True,
        null=True
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    status = models.CharField(
        choices=PR_STATUS_CHOICES,
        max_length=10,
        verbose_name=_('Status')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )

    class Meta:
        verbose_name = _('Purchase request')
        verbose_name_plural = _('Purchase requests')
        app_label = 'inventory'

    def __str__(self):
        return '#%s (%s)' % (self.user_id if self.user_id else self.id, self.issue_date)

    @property
    def supplier(self):
        return self.supplier_contact.organization if self.supplier_contact else None

class PurchaseRequestItem(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, related_name='items',
                                         verbose_name=_('Purchase request'))
    item = models.ForeignKey('inventory.Item', verbose_name=_('Item'))
    qty = models.PositiveIntegerField(verbose_name=_('Quantity'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notes'))

    def __str__(self):
        return "{purchase_request}: {item}".format(purchase_request=self.purchase_request,
                                                   item=self.item)

    class Meta:
        verbose_name = _('Purchase request item')
        verbose_name_plural = _('Purchase request items')
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
    status = models.CharField(choices=PO_STATUS_CHOICES, max_length=10, verbose_name=_('Status'))

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
    item = models.ForeignKey('inventory.Item', verbose_name=_('Item'))
    agreed_price = models.PositiveIntegerField(null=True, blank=True,
                                               verbose_name=_('Agreed price'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    status = models.ForeignKey(PurchaseOrderItemStatus, null=True, blank=True,
                               verbose_name=_('Status'))
    qty = models.PositiveIntegerField(verbose_name=_('Quantity'))
    received_qty = models.PositiveIntegerField(default=0, null=True, blank=True,
                                               verbose_name=_('received'))

    def __str__(self):
        return str(self.item)

    class Meta:
        verbose_name = _('Purchase order item')
        verbose_name_plural = _('Purchase order items')
        app_label = 'inventory'

# register(PurchaseRequestStatus, _('Purchase request status'), ['name'])
# register(PurchaseRequest, _('Purchase request'), ['user_id', 'id', 'budget', 'required_date',
# 'status__name', 'originator'])
# register(PurchaseRequestItem, _('Purchase request item'), ['item_template__description', 'qty',
#  'notes'])
# register(PurchaseOrderStatus, _('Purchase order status'), ['name'])
# register(PurchaseOrderItemStatus, _('Purchase order item status'), ['name'])
# register(PurchaseOrder, _('Purchase order'), ['user_id', 'id', 'required_date', 'status__name',
#  'supplier__name', 'notes'])
# register(PurchaseOrderItem, _('Purchase order item'), ['item_template__description', 'qty'])
