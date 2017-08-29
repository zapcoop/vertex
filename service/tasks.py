import email
from django.core.exceptions import PermissionDenied
from django.template import Context
from django.db import transaction
from django_mailbox.models import Message
import html2text

from vertex.celery import app
import vertex.rules
from service.models import Ticket, TicketSubscriber, Update, EmailTemplate
from contacts.models import EmailAddress, EmailDomain


@app.task(routing_key='vertex', ignore_result=True)
def create_ticket_from_email_message(message_pk):
    with transaction.atomic():
        message = Message.objects.get(pk=message_pk)
        sender = EmailAddress.objects.filter(email_address=message.from_address[0]).first()
        team = message.mailbox.team

        ticket = Ticket(
            title=message.subject,
            priority=5,
            message_id=message.message_id
        )

        if not message.html:
            ticket.description = message.text
            ticket.description_is_plain = True
        else:
            text_maker = html2text.HTML2Text()
            text_maker.escape_snob = True
            ticket.description = text_maker.handle(message.html)

        if sender and sender.person:
            ticket.created_by = sender.person
            ticket.signaled_by = sender.person

        if sender and sender.organization:
            ticket.organization = sender.organization
        else:
            ticket.organization = _organization_from_domain(message.from_address[0].split('@')[1])

        ticket.save()  # TODO: send a confirmation email
        ticket.teams.add(team)
        add_subscribers_from_email(message, ticket)


@app.task(routing_key='vertex', ignore_result=True)
def update_ticket_from_email_message(message_pk, hash_id):
    message = Message.objects.get(pk=message_pk)
    sender = EmailAddress.objects.filter(email_address=message.from_address[0]).first()
    pk, = Ticket.HASHIDS.decode(hash_id)
    ticket = Ticket.objects.filter(pk=pk).first()

    if (ticket is None) or (sender is None):
        template = EmailTemplate.objects.get(slug='no_such_ticket')
        template.send_service_email_bilingual(
            context=Context(),
            from_mailbox=message.mailbox,
            to=message.from_address[0],
            cc=None,
            in_reply_to_message=message
        )
    
    elif has_update_permission(sender, ticket):
        with transaction.atomic():
            if message.html:
                text_maker = html2text.HTML2Text()
                text_maker.escape_snob = True
                body = text_maker.handle(message.html)
                Update.objects.create(
                    ticket=ticket,
                    person=sender.person,
                    body=body,
                    body_is_plaintext=False,
                    message_id=message.message_id
                )
            else:
                Update.objects.create(
                    ticket=ticket,
                    person=sender.person,
                    body=message.text,
                    body_is_plaintext=True,
                    message_id=message.message_id
                )
            add_subscribers_from_email(message, ticket)

    elif has_view_permission(sender, ticket):
        template = EmailTemplate.objects.get(slug='insufficient_permissions')
        template.send_service_email_bilingual(
            context=Context(),
            from_mailbox=message.mailbox,
            to=message.from_address[0],
            cc=None,
            in_reply_to_message=message
        )

    else:
        template = EmailTemplate.objects.get(slug='no_such_ticket')
        template.send_service_email_bilingual(
            context=Context(),
            from_mailbox=message.mailbox,
            to=message.from_address[0],
            cc=None,
            in_reply_to_message=message
        )


def has_update_permission(sender, ticket):
    try:
        subscription = TicketSubscriber.objects.get(email_address=sender, ticket=ticket)
    except TicketSubscriber.DoesNotExist:
        pass
    else:
        return subscription.can_update

    if sender.person:
        try:
            return vertex.rules.has_perm('service.change_ticket', sender.person, ticket)
        except PermissionDenied:
            return False

    elif sender.organization:
        return ticket.organization == sender.organization

    return False


def has_view_permission(sender, ticket):
    try:
        subscription = TicketSubscriber.objects.get(email_address=sender, ticket=ticket)
    except TicketSubscriber.DoesNotExist:
        pass
    else:
        return subscription.can_view

    if sender.person:
        try:
            return vertex.rules.has_perm('service.view_ticket', sender.person, ticket)
        except PermissionDenied:
            return False
    elif sender.organization:
        return ticket.organization == sender.organization

    return False


def _organization_from_domain(domain_name):
    try:
        domain = EmailDomain.objects.get(domain_name__iexact=domain_name)
        return domain.organization
    except EmailDomain.DoesNotExist:
        return None


def add_subscribers_from_email(message, ticket):
    subscriber_emails = subscribers_specified_in_message(message)
    ticket_subscribers = list()
    for email_address in subscriber_emails:
        ticket_subscribers.append(
            TicketSubscriber(email_address=email_address, ticket=ticket, can_view=True)
        )
    TicketSubscriber.objects.bulk_create(ticket_subscribers)


def subscribers_specified_in_message(msg):  # TODO make this case-insensitive
    return EmailAddress.objects.filter(email_address__in=(msg.from_address + get_cc_addresses(msg)))


def get_cc_addresses(msg):
    cc_addresses = list()
    cc_headers = msg.get_email_object().get_all('CC')
    if cc_headers is None:
        return []
    for (name, address) in email.utils.getaddresses(cc_headers):
        cc_addresses.append(address)
    return cc_addresses
