from vertex.filters import IdListFilterSet
from ..models import Update


class UpdateFilterSet(IdListFilterSet):

    class Meta:
        model = Update
