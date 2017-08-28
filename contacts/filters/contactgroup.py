from noss.filters import IdListFilterSet
from ..models import ContactGroup


class ContactGroupFilterSet(IdListFilterSet):

    class Meta:
        model = ContactGroup
