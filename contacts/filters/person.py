from noss.filters import IdListFilterSet
from ..models import Person


class PersonFilterSet(IdListFilterSet):

    class Meta:
        model = Person
