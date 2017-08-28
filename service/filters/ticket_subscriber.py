from noss.filters import IdListFilterSet
from ..models import TicketSubscriber


class TicketSubscriberFilterSet(IdListFilterSet):

    class Meta:
        model = TicketSubscriber
