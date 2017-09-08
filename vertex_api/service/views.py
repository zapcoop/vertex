import copy
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import exceptions, status
from vertex.api.permissions import RestrictedObjectLevelPermissions
from rest_framework_json_api.utils import format_relation_name
from rest_framework_json_api.views import RelationshipView
from .models import Ticket, Update, Team
from .serializers import CloseTicketSerializer

custom_perms_map = copy.deepcopy(RestrictedObjectLevelPermissions.perms_map)
custom_perms_map['POST'] = ['service.directly_close_ticket']


class SpecialPermissions(RestrictedObjectLevelPermissions):
    perms_map = custom_perms_map


class CloseTicketView(GenericAPIView):
    queryset = Ticket.objects
    serializer_class = CloseTicketSerializer
    lookup_url_kwarg = 'pk'
    resource_name = format_relation_name('Ticket')
    permission_classes = (SpecialPermissions, )

    def get_queryset(self):
        return self.queryset.filter(signaled_by=self.request.user.person)

    def get_serializer_context(self):
        context = super(CloseTicketView, self).get_serializer_context()
        context.update(
            person=self.request.user.person,
            ticket=self.get_object()
        )
        return context

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not self.request.user.has_perm('service.directly_close_ticket', ticket):
            raise exceptions.PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateRelationshipView(RelationshipView):
    queryset = Update.objects


class TicketRelationshipView(RelationshipView):
    queryset = Ticket.objects


class TeamRelationshipView(RelationshipView):
    queryset = Team.objects
