from django.db import models
from django.utils.translation import ugettext_lazy as _
from noss import rules

from noss.models import AbstractDatedModel
from noss.rules.predicates import has_django_permission, is_superuser, is_staff

__author__ = 'jsenecal'


class TicketSubscriber(AbstractDatedModel, models.Model):
    """
    Often, there are people who wish to follow a ticket who aren't the
    person who originally submitted it. This model provides a way for those
    people to follow a ticket.
    In this circumstance, a 'person' could be either an e-mail address or
    an existing system user.
    """

    ticket = models.ForeignKey(
        'service.Ticket',
        verbose_name=_('Ticket'),
        related_name='subscribers'
        )

    email_address = models.ForeignKey(
        'contacts.EmailAddress',
        help_text=_('Where to send updates for this ticket?'),
        verbose_name=_('Email address'),
        related_name='ticket_subscriptions'
        )

    can_view = models.BooleanField(
        _('Can View Ticket?'),
        blank=True,
        default=False,
        help_text=_('Can this person view the ticket details?'),
        )

    can_update = models.BooleanField(
        _('Can Update Ticket?'),
        blank=True,
        default=False,
        help_text=_('Can this person change/update the ticket?'),
        )

    def __str__(self):
        return u'%s for %s' % (self.email_address.email_address, self.ticket.title)

    class Meta:
        app_label = 'service'


# TODO: refine these permissions (e.g. maybe someone with read access to a given ticket can see the subscriber list)
rules.add_perm('service.view_ticketsubscriber', is_superuser | is_staff)
rules.add_perm('service.add_ticketsubscriber', is_superuser | is_staff & has_django_permission('service.add_ticketsubscriber'))
rules.add_perm('service.change_ticketsubscriber', is_superuser | is_staff & has_django_permission('service.change_ticketsubscriber'))
rules.add_perm('service.delete_ticketsubscriber', is_superuser | is_staff & has_django_permission('service.delete_ticketsubscriber'))
