__author__ = 'jsenecal'

import rest_framework_filters as filters

from noss.filters import IdListFilterSet
from contacts.models import EmailAddress


class EmailAddressFilterSet(IdListFilterSet):
    ids = filters.AllLookupsFilter(name="id")
    email_address = filters.AllLookupsFilter(name="email_address")
    person = filters.AllLookupsFilter(name="person")
    organization = filters.AllLookupsFilter(name="organization")
    information_type = filters.AllLookupsFilter(name="information_type")

    class Meta:
        model = EmailAddress
        fields = ['id', 'email_address', 'person', 'organization', 'information_type']