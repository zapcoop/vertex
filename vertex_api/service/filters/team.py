from vertex.filters import IdListFilterSet
from ..models import Team


class TeamFilterSet(IdListFilterSet):

    class Meta:
        model = Team
