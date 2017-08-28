import rest_framework_filters as filters

from noss.filters import IdListFilterSet
from contacts.models import Organization


class OrganizationFilterSet(IdListFilterSet):
    parent = filters.AllLookupsFilter(name="parent__name")
    notes = filters.AllLookupsFilter(name="notes")
    name = filters.AllLookupsFilter(name="name")
    nick = filters.AllLookupsFilter(name="nickname")
    reference = filters.AllLookupsFilter(name="reference")
    people = filters.AllLookupsFilter(name="people")
    administrators = filters.AllLookupsFilter(name="administrators")

    class Meta:
        model = Organization
        fields = ['notes', 'name', 'nickname', 'reference', 'parent', 'people', 'administrators']