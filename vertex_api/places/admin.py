from django.contrib import admin

from places.models import Place


class PlaceTypesFieldListFilter(admin.SimpleListFilter):
    """This is a list filter based on the values
    from a model's `keywords` ArrayField. """

    title = 'Place Types'
    parameter_name = 'place_types'

    def lookups(self, request, model_admin):
        # Very similar to our code above, but this method must return a
        # list of tuples: (lookup_value, human-readable value). These
        # appear in the admin's right sidebar

        place_types = Place.objects.values_list("place_types", flat=True)
        place_types = [(kw, kw) for sublist in place_types for kw in sublist if kw]
        place_types = sorted(set(place_types))
        return place_types

    def queryset(self, request, queryset):
        # when a user clicks on a filter, this method gets called. The
        # provided queryset with be a queryset of Items, so we need to
        # filter that based on the clicked keyword.

        lookup_value = self.value()  # The clicked keyword. It can be None!
        if lookup_value:
            # the __contains lookup expects a list, so...
            queryset = queryset.filter(place_types__contains=[lookup_value])
        return queryset


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    readonly_fields = ('point',)

    list_display = ('formatted_address', 'place_types')
    list_filter = (PlaceTypesFieldListFilter,)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is the case when obj is already created i.e. it's an edit
            return self.readonly_fields + ('google_place_id', 'place_types')
        else:
            return self.readonly_fields
