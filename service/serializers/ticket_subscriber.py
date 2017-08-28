from rest_framework_json_api import serializers, relations

from ..models import TicketSubscriber, Ticket
from contacts.models import EmailAddress


class TicketSubscriberSerializer(serializers.HyperlinkedModelSerializer):
    ticket = relations.ResourceRelatedField(queryset=Ticket.objects)
    email_address = relations.ResourceRelatedField(queryset=EmailAddress.objects)

    class Meta:
        model = TicketSubscriber
        fields = ('ticket', 'email_address', 'can_view', 'can_update')
