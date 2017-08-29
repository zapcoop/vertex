from rest_framework import viewsets
from vertex.api.permissions import RestrictedObjectLevelPermissions

from ..serializers import TicketSubscriberSerializer
from ..models import TicketSubscriber
from ..filters import TicketSubscriberFilterSet


class TicketSubscriberViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSubscriberSerializer
    queryset = TicketSubscriber.objects.all()
    permission_classes = (RestrictedObjectLevelPermissions,)
    filter_class = TicketSubscriberFilterSet
