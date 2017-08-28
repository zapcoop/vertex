from django.apps import apps
from django.db.models import Count
import rules


@rules.predicate
def has_ticket_object_view_rights(person, ticket):
    """
    True if `person` has special view rights to this ticket instance.

    This includes the person who created or signaled the ticket and, if the ticket is associated
    with an organization, admins and department heads of that organization.
    """
    TicketSubscriber = apps.get_model('service', 'TicketSubscriber')
    Ticket = apps.get_model('service', 'Ticket')
    if not ticket:
        return (person.created_tickets.exists() or person.originated_tickets.exists() or
         TicketSubscriber.objects.filter(person=person).exists() or
         Ticket.objects.filter(organization__in=person.managed_organizations.all()) or
         Ticket.objects.filter(organization__departments__in=person.managed_departments.all()))

    if ticket.created_by == person or ticket.signaled_by == person:
        return True

    elif ticket.organization:
        return (person.managed_organizations.filter(pk=ticket.organization.pk).exists() or
                person.managed_departments.filter(organization=ticket.organization))

    return False


@rules.predicate
def has_ticket_view_subscription(person, ticket):
    if not ticket:
        return False
    return apps.get_model('service', 'TicketSubscriber').objects.filter(
        email_address__in=person.email_addresses.all()).filter(can_view=True)


@rules.predicate
def has_ticket_change_subscription(person, ticket):
    if not ticket:
        return False
    return apps.get_model('service', 'TicketSubscriber').objects.filter(
        email_address__in=person.email_addresses.all()).filter(can_update=True)


@rules.predicate
def is_ticket_signaler(person, ticket):
    if not ticket:
        return person.originated_tickets.exists()
    return person == ticket.signaled_by
