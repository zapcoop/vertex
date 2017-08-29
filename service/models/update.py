from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from vertex.models import AbstractDatedModel
from vertex import rules
from vertex.rules.predicates import has_django_permission, is_staff, is_superuser

from .ticket import Ticket


UPDATE_TYPES = (
    ('action', _('Email Message Received')),
    ('change', _('Email Message Sent')),
    ('communication', _('Note added')),
    ('note', _('Message')),
    ('ticket_change', _('Ticket change')),
    ('ticket_assigned', _('Ticket assigned')),
)

UPDATE_TEXT = (
    ('email_received', _('Email received from {person}')),
    (Ticket.IN_PROGRESS_STATUS, _('In progress')),
    (Ticket.WAITING_FOR_CUSTOMER_STATUS, _('Waiting for customer')),
    (Ticket.ON_HOLD_STATUS, _('On hold')),
    (Ticket.RESOLVED_STATUS, _('Resolved')),
    (Ticket.FOLLOW_UP_SENT_STATUS, _('Follow-up sent')),
    (Ticket.REOPENED_STATUS, _('Re-opened')),
    (Ticket.CLOSED_STATUS, _('Closed')),
    (Ticket.DUPLICATE_STATUS, _('Duplicate')),
)


class Update(AbstractDatedModel, models.Model):
    """
    An update is a comment, action, and/or a set of changes to the ticket.
    """

    ticket = models.ForeignKey(
        'service.Ticket',
        verbose_name=_('Ticket'),
        editable=False,
        related_name='updates'
    )

    display_time = models.DateTimeField(
        _('Date'),
        default=timezone.now
    )

    body = models.TextField(
        _('Body'),
        blank=True
    )

    body_is_plaintext = models.BooleanField(default=False)

    person = models.ForeignKey(
        'contacts.Person',
        verbose_name=_('Person'),
        null=True,
        editable=False
    )

    email_address = models.ForeignKey(
        'contacts.EmailAddress',
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    duration = models.DurationField(
        _('Duration'),
        blank=True,
        null=True
    )

    billable_hours = models.DurationField(
        _('Billable hours'),
        blank=True,
        null=True
    )

    message_id = models.CharField(max_length=255, blank=True, editable=False)

    class Meta:
        ordering = ['display_time']
        verbose_name = _('Update')
        verbose_name_plural = _('Updates')

    def __str__(self):
        return '{type} by {person} on {ticket}'.format(type=self.type, person=self.person, ticket=self.ticket)

    @property
    def type(self):
        if self.duration is not None:
            return _('Action')
        else:
            return _('Comment')

    @property
    def ticket_changes(self):
        for ticket_change in self.ticketchange_set.all():
            yield {
                'field_name': ticket_change.field,
                'old_value': ticket_change.old_value,
                'new_value': ticket_change.new_value
            }

    @property
    def editable(self):
        age = timezone.now() - self.created_at
        return age < timedelta(seconds=settings.TICKET_UPDATE_ALLOW_EDIT_DURATION)


rules.add_perm('service.view_update', is_superuser | is_staff)
rules.add_perm('service.add_update', is_superuser | is_staff & has_django_permission('service.add_update'))
rules.add_perm('service.change_update', is_superuser | is_staff & has_django_permission('service.change_update'))
rules.add_perm('service.delete_update', is_superuser | is_staff & has_django_permission('service.delete_update'))
