from django.db.models import QuerySet

from rest_framework import viewsets

from vertex.api.permissions import RestrictedObjectLevelPermissions
from service.models import Ticket
from service.serializers import TicketSerializer
from ..filters import TicketFilterSet


class TicketViewSet(viewsets.ModelViewSet):

    queryset = Ticket.objects
    serializer_class = TicketSerializer
    permission_classes = (RestrictedObjectLevelPermissions, )
    filter_class = TicketFilterSet
    filter_fields = ('id',)

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Ticket.objects
        elif self.request.user.is_staff:
            queryset = Ticket.objects
        else:
            queryset = Ticket.objects.filter(organization__in=self.request.user.person.organizations.all())
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()

    def perform_create(self, serializer):  # TODO: tickets can be created by email...
        serializer.save(created_by=self.request.user.person)
