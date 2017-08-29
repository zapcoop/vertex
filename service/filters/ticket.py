from vertex.filters import IdListFilterSet
from ..models import Ticket


class TicketFilterSet(IdListFilterSet):

    class Meta:
        model = Ticket
