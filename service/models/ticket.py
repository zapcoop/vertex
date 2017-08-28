from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMIntegerField, transition
from hashids import Hashids

from contacts.rules.organization import is_object_organization_admin
from noss import rules
from noss.models import AbstractDatedModel
from noss.rules.predicates import has_django_permission, is_staff, is_superuser
from tags.models import AbstractTaggedModel
from ..rules.department import is_ticket_team_member
from ..rules.ticket import (has_ticket_object_view_rights, has_ticket_change_subscription,
                            has_ticket_view_subscription, is_ticket_signaler)

__author__ = 'jsenecal'

TICKET_ID_SALT = "NOSS-service-app"
TICKET_ID_ALPHABET = 'ABCDEFGHJKLNPQRSUVXYZ012356789'


class Ticket(AbstractTaggedModel, AbstractDatedModel):
    """
    To allow a ticket to be entered as quickly as possible, only the
    bare minimum fields are required. These basically allow us to
    sort and manage the ticket. The user can always go back and
    enter more information later.
    A good example of this is when a customer is on the phone, and
    you want to give them a ticket ID as quickly as possible. You can
    enter some basic info, save the ticket, give the customer the ID
    and get off the phone, then add in further detail at a later time
    (once the customer is not on the line).
    Update that assigned_to is optional - unassigned tickets are displayed on
    the dashboard to prompt users to take ownership of them.
    """

    NEW_STATUS = 0
    IN_PROGRESS_STATUS = 1
    WAITING_FOR_CUSTOMER_STATUS = 2
    ON_HOLD_STATUS = 3
    RESOLVED_STATUS = 4
    FOLLOW_UP_SENT_STATUS = 5
    REOPENED_STATUS = 6
    CLOSED_STATUS = 7
    DUPLICATE_STATUS = 8

    STATUS_CHOICES = (
        (NEW_STATUS, _('New')),
        (IN_PROGRESS_STATUS, _('In progress')),
        (WAITING_FOR_CUSTOMER_STATUS, _('Waiting for customer')),
        (ON_HOLD_STATUS, _('On hold')),
        (RESOLVED_STATUS, _('Resolved')),
        (FOLLOW_UP_SENT_STATUS, _('Follow-up sent')),
        (REOPENED_STATUS, _('Re-opened')),
        (CLOSED_STATUS, _('Closed')),
        (DUPLICATE_STATUS, _('Duplicate')),
    )

    PRIORITY_CHOICES = (
        (1, _('P1. Critical')),
        (2, _('P2. High')),
        (3, _('P3. Normal')),
        (4, _('P4. Low')),
        (5, _('P5. Very Low')),
    )

    HASHIDS = Hashids(
        salt=TICKET_ID_SALT,
        min_length=5,
        alphabet=TICKET_ID_ALPHABET
    )

    title = models.CharField(
        _('Title'),
        max_length=200,
    )

    teams = models.ManyToManyField(
        'service.Team',
        related_name='tickets'
    )

    signaled_by = models.ForeignKey(
        'contacts.Person',
        related_name='originated_tickets',
        blank=True,
        null=True,
        verbose_name=_('Signaled by'),
    )

    # note: null is true because sometimes a ticket created from email initially has no organization;
    # however blank is False, which means that a ticket created from the api (or frontend) must be
    # associated with an organization
    organization = models.ForeignKey(
        'contacts.Organization',
        null=True
    )

    created_by = models.ForeignKey(
        'contacts.Person',
        related_name='created_tickets',
        blank=True,
        null=True,
        verbose_name=_('Created by'),
    )

    assigned_to = models.ForeignKey(
        'contacts.Person',
        related_name='assigned_tickets',
        blank=True,
        null=True,
        verbose_name=_('Assigned to'),
    )

    status = FSMIntegerField(
        _('Status'),
        default=NEW_STATUS,
        choices=STATUS_CHOICES,
        protected=True,
        editable=False
    )

    description = models.TextField(
        _('Description'),
        blank=True,
        null=True,
        help_text=_('The content of the query.'),
    )

    description_is_plain = models.BooleanField(default=False)

    resolution = models.TextField(
        _('Resolution'),
        blank=True,
        null=True,
        help_text=_('The resolution provided by our staff.'),
    )

    priority = models.IntegerField(
        _('Priority'),
        choices=PRIORITY_CHOICES,
        help_text=_('1 = Highest Priority, 5 = Low Priority'),
    )

    signaled_date = models.DateTimeField(
        default=timezone.now
    )

    due_date = models.DateTimeField(
        _('Due on'),
        blank=True,
        null=True,
    )

    last_escalation = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text=_('The date this ticket was last escalated - updated automatically'),
    )

    # message_id is the MessageId of the email message that created this Ticket (if applicable)
    message_id = models.CharField(
        max_length=255,
        default='',
        editable=False,
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        editable=False,
        related_name='children'
    )

    duplicate_of = models.ForeignKey(
        'self',
        null=True,
        related_name='duplicates',
        editable=False
    )

    @property
    def assigned_person_display(self):
        """ Custom property to allow us to easily print 'Unassigned' if a
        ticket has no owner, or the person's name if it's assigned. """
        if not self.assigned_to:
            return _('Unassigned')
        else:
            return self.assigned_to.full_name

    @property
    def ticket_id(self):
        """ A user-friendly ticket ID, which is a combination of ticket ID
        and department slug. This is generally used in e-mail subjects. """

        return "[Ticket:%s]" % (self.ticket_for_url)

    @property
    def ticket_for_url(self):
        """ A URL-friendly ticket ID, used in links. """
        return self.HASHIDS.encode(self.id)

    @property
    def priority_css_class(self):
        """
        Return the boostrap class corresponding to the priority.
        """
        if self.priority == 2:
            return "warning"
        elif self.priority == 1:
            return "danger"
        else:
            return ""

    def is_closed(self):
        return self.status not in OPEN_STATUSES

    def can_be_resolved(self):
        """
        Returns a boolean.
        True = any dependencies are resolved
        False = There are non-resolved dependencies
        """
        return (self.parent is None or self.parent.is_closed()) and \
               (self.duplicate_of is None or self.duplicate_of.is_closed())

    def is_assigned(self):
        return self.assigned_to is not None

    def is_duplicate(self):
        return self.duplicate_of is not None

    @transition(field=status, source=NEW_STATUS, target=IN_PROGRESS_STATUS, conditions=(is_assigned,))
    def open(self):
        pass  # may trigger notification email in the future

    @transition(field=status, source=REOPENED_STATUS, target=IN_PROGRESS_STATUS)
    def resume(self):
        pass

    @transition(field=status, source=WAITING_FOR_CUSTOMER_STATUS, target=IN_PROGRESS_STATUS)
    def process_customer_reply(self):
        pass  # maybe trigger a notification to the person assigned to the ticket?

    @transition(field=status, source=ON_HOLD_STATUS, target=IN_PROGRESS_STATUS)
    def remove_hold(self):
        pass

    @transition(field=status, source=IN_PROGRESS_STATUS, target=ON_HOLD_STATUS)
    def put_on_hold(self):
        pass

    @transition(field=status, source=IN_PROGRESS_STATUS, target=DUPLICATE_STATUS, conditions=(is_duplicate,))
    def mark_duplicate(self):
        pass

    @transition(field=status, source=IN_PROGRESS_STATUS, target=WAITING_FOR_CUSTOMER_STATUS)
    def wait_for_customer(self):
        pass

    @transition(field=status, source=IN_PROGRESS_STATUS, target=RESOLVED_STATUS, conditions=(can_be_resolved,))
    def resolve(self):
        pass

    @transition(field=status, source=RESOLVED_STATUS, target=FOLLOW_UP_SENT_STATUS)
    def send_follow_up_email(self):
        pass  # TODO : send the actual email

    @transition(field=status, source=FOLLOW_UP_SENT_STATUS, target=CLOSED_STATUS)
    def close(self):
        pass

    @transition(field=status, source=FOLLOW_UP_SENT_STATUS, target=REOPENED_STATUS)
    def reopen(self):
        pass

    @transition(field=status, source='*', target=CLOSED_STATUS, conditions=[lambda self: not self.is_closed()])
    def close_by_signaler(self):
        pass

    class Meta:
        get_latest_by = "created_at"
        ordering = ('id',)
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        app_label = 'service'

    def __str__(self):
        return u'%s %s' % (self.id, self.title)


OPEN_STATUSES = (
    Ticket.NEW_STATUS,
    Ticket.IN_PROGRESS_STATUS,
    Ticket.WAITING_FOR_CUSTOMER_STATUS,
    Ticket.ON_HOLD_STATUS,
    Ticket.RESOLVED_STATUS,
    Ticket.FOLLOW_UP_SENT_STATUS,
    Ticket.REOPENED_STATUS
)

rules.add_perm('service.view_ticket',
               is_superuser |
               is_staff |
               is_ticket_team_member |
               has_ticket_object_view_rights |
               has_ticket_view_subscription |
               is_ticket_signaler)
rules.add_perm('service.add_ticket',
               is_superuser |
               (is_staff & has_django_permission('service.add_ticket')))
rules.add_perm('service.change_ticket',
               is_superuser |
               is_object_organization_admin |
               is_ticket_team_member |
               has_ticket_change_subscription |
               (is_staff & has_django_permission('service.change_ticket')))
rules.add_perm('service.delete_ticket',
               is_superuser |
               is_ticket_team_member |
               (is_staff & has_django_permission('service.delete_ticket')))
rules.add_perm('service.directly_close_ticket', is_ticket_signaler)
