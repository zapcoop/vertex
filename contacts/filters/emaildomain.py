from noss.filters import IdListFilterSet
from ..models import EmailDomain


class EmailDomainFilterSet(IdListFilterSet):

    class Meta:
        model = EmailDomain
