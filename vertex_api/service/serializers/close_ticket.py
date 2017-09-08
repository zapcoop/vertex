from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from service.models import Ticket, Update, TicketChange


class CloseTicketSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate(self, attrs):
        ticket = self.context['ticket']
        if ticket.is_closed():
            raise serializers.ValidationError(_("This ticket is already closed."))
        return attrs

    def save(self, **kwargs):
        ticket = self.context['ticket']
        person = self.context['person']

        with transaction.atomic():
            update = Update.objects.create(
                ticket=ticket,
                body=self.validated_data.get('comment', ''),
                person=person
            )

            TicketChange.objects.create(
                update=update,
                field='status',
                old_value=ticket.status,
                new_value=Ticket.CLOSED_STATUS
            )

            ticket.close_by_signaler()
            ticket.save()
