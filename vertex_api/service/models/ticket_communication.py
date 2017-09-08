from django.db import models

from django_mailbox.models import Message, Mailbox

from . import Ticket, TicketSubscriber


class TicketCommunication(models.Model):

    message = models.OneToOneField(Message)
    ticket = models.ForeignKey(Ticket)

    @property
    def message_id(self):
        return self.message.message_id

    @property
    def mailboxes(self):
        messages = Message.objects.filter(message_id=self.message_id).select_related('mailbox')
        return (message.mailbox for message in messages)
