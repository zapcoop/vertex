from noss.filters import IdListFilterSet
from ..models import PhoneNumber


class PhoneNumberFilterSet(IdListFilterSet):

    class Meta:
        model = PhoneNumber
