from django.contrib import admin

from inventory.models import (
    State,
    ItemState,
    Item,
    ItemGroup
)

from inventory.models import (
    Inventory,
    ItemTemplate,
    InventoryCheckPoint,
    InventoryCPQty,
    InventoryTransaction,
    Log
)

from inventory.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
    PurchaseOrderItemStatus,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseRequestStatus
)

admin.site.register(State)
admin.site.register(ItemState)
admin.site.register(Item)
admin.site.register(ItemGroup)


class ItemTemplateAdmin(admin.ModelAdmin):
    filter_horizontal = ('supplies', 'suppliers')


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


admin.site.register(PurchaseRequestStatus)
admin.site.register(PurchaseRequest, PurchaseRequestAdmin)
admin.site.register(PurchaseRequestItem)
admin.site.register(PurchaseOrderStatus)
admin.site.register(PurchaseOrderItemStatus)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseOrderItem)

admin.site.register(Log)
admin.site.register(ItemTemplate, ItemTemplateAdmin)
admin.site.register(Inventory)
