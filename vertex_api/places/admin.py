from django.contrib import admin

from places.models import (
    Place,
    AddressComponentThrough
)


class AddressComponentInline(admin.TabularInline):
    model = AddressComponentThrough
    extra = 0
    verbose_name = 'Address Component'
    verbose_name_plural = 'Address Components'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is the case when obj is already created i.e. it's an edit
            return self.readonly_fields + ('order', 'address_component')
        else:
            return self.readonly_fields


class PlaceAdmin(admin.ModelAdmin):
    inlines = (AddressComponentInline,)
    readonly_fields = ('point',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is the case when obj is already created i.e. it's an edit
            return self.readonly_fields + ('raw_address', 'google_place_id', 'place_type')
        else:
            return self.readonly_fields


admin.site.register(Place, PlaceAdmin)
