from django.contrib import admin

from places.models import (
    Place,
    AddressComponentThrough
)


class AddressComponentInline(admin.TabularInline):
    model = AddressComponentThrough
    extra = 0


class PlaceAdmin(admin.ModelAdmin):
    inlines = (AddressComponentInline,)
    readonly_fields = ('lat_long', 'place_type')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is the case when obj is already created i.e. it's an edit
            return self.readonly_fields + ('raw_address', 'google_place_id')
        else:
            return self.readonly_fields


admin.site.register(Place, PlaceAdmin)
