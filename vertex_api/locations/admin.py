from django.contrib import admin
from locations.models import Location,Site,Floor,Room


@admin.register(Location)
class PlaceAdmin(admin.ModelAdmin):
    readonly_fields = ('place',)

    list_display = ('place',)


admin.site.register(Site)
admin.site.register(Floor)
admin.site.register(Room)
