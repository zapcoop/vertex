from noss.filters import IdListFilterSet
from ..models import URL


class URLFilterSet(IdListFilterSet):

    class Meta:
        model = URL
