from django.contrib import admin

from inventory.models import (
    State,
    AssetState,
    Asset,
    AssetGroup
)

from inventory.models import (
    Stockroom,
    Item,
    InventoryCheckPoint,
    InventoryCPQty,
    InventoryTransaction,
)

from inventory.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderItemStatus,
    PurchaseRequest,
    PurchaseRequestItem

)

admin.site.register(State)
admin.site.register(AssetState)
admin.site.register(Asset)
admin.site.register(AssetGroup)


class ItemAdmin(admin.ModelAdmin):
    filter_horizontal = ('parts', 'suppliers')


class PurchaseRequestItemInline(admin.StackedInline):
    model = PurchaseRequestItem
    extra = 1
    classes = ('collapse-open',)
    allow_add = True


class PurchaseRequestAdmin(admin.ModelAdmin):
    inlines = [PurchaseRequestItemInline]


class PurchaseOrderItemInline(admin.StackedInline):
    model = PurchaseOrderItem
    extra = 1
    classes = ('collapse-open',)
    allow_add = True


class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [PurchaseOrderItemInline]


admin.site.register(PurchaseRequest, PurchaseRequestAdmin)
admin.site.register(PurchaseRequestItem)
admin.site.register(PurchaseOrderItemStatus)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseOrderItem)

admin.site.register(Item, ItemAdmin)
admin.site.register(Stockroom)
