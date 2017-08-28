import datetime
import os
import shutil
import copy
from mailbox import Maildir
import json
from unittest import mock
import pytz

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.conf import settings

from rest_framework.test import APITestCase
from rest_framework_json_api.utils import format_relation_name
from rest_framework import status

from django_mailbox.models import Mailbox

from service.models import Ticket, Update, Team, TicketSubscriber
from contacts.models import Organization, Person, EmailDomain, EmailAddress
import service.tasks
from noss.utils.test import VerifiedForcedAuthenticationMixin

MAILDIR_PATH = '/tmp/noss_test_maildir'


class TestUpdateModel(TestCase):

    def setUp(self):
        organization, created = Organization.objects.get_or_create(name='Example Corp')

        mailbox = Mailbox.objects.create(
            name='test_mailbox',
            uri='imap://test_mailbox:badpassword@leifurpc.localdomain?archive=Archive',
            from_email='test_mailbox@leifurpc.localdomain'
        )

        self.person, created = Person.objects.get_or_create(
            first_name='Jane',
            last_name='Doe'
        )
        self.team, created = Team.objects.get_or_create(
            name='Example Department',
            slug='example_dept',
            mailbox=mailbox
        )
        self.ticket, created = Ticket.objects.get_or_create(
            title='Test Ticket',
            organization=organization,
            priority=4
        )
        self.ticket.teams.add(self.team)

    def test_update_type(self):
        action_update, created = Update.objects.get_or_create(
            ticket=self.ticket,
            body='Lorem ipsum dolor sit amet, consectetur adipiscing elit',
            duration=datetime.timedelta(hours=3),
            billable_hours=datetime.timedelta(hours=2),
            person=self.person
        )
        comment_update, created = Update.objects.get_or_create(
            ticket=self.ticket,
            body='sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
            person=self.person
        )

        self.assertTrue(action_update.type == 'Action')
        self.assertTrue(comment_update.type == 'Comment')


class TestTicketViewSet(TestCase):

    def setUp(self):
        self.organization, created = Organization.objects.get_or_create(name='Example Corp')

        mailbox = Mailbox.objects.create(
            name='test_mailbox',
            uri='imap://test_mailbox:badpassword@leifurpc.localdomain?archive=Archive',
            from_email='test_mailbox@leifurpc.localdomain'
        )

        self.team, created = Team.objects.get_or_create(
            name='Example Department',
            slug='example_dept',
            mailbox=mailbox
        )
        self.superuser = User.objects.create_superuser(username='super', email='super@example.org', password='badpassword')
        Person.objects.create(user=self.superuser)

        self.person, created = Person.objects.get_or_create(first_name='Jane', last_name='Doe')
        self.ticket, created = Ticket.objects.get_or_create(
            title='Testing 123 Ticket',
            team=self.team,
            organization=self.organization,
            priority=4
        )


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, CELERY_ALWAYS_EAGER=True)
class TestServiceEmailTasks(TestCase):

    maildir = Maildir(MAILDIR_PATH)

    _sender_email = 'sender@examplecorp.com'
    _recipient_email = 'recipient@example.org'
    _cc_emails = ['cc1@example.org', 'cc2@example.org']

    def setUp(self):
        organization, created = Organization.objects.get_or_create(name='Example Corp')

        self.mailbox = Mailbox.objects.create(
            name='test_mailbox',
            uri='maildir://' + MAILDIR_PATH,
            from_email='test_mailbox@noss.com'
        )

        # clear any pre-existing messages in the local mailbox
        self.maildir.clear()

        self.team, created = Team.objects.get_or_create(
            name='Example Department',
            slug='example_dept',
            mailbox=self.mailbox
        )

        self.ticket, created = Ticket.objects.get_or_create(
            title='Testing 123 Ticket',
            organization=organization,
            priority=4
        )
        self.ticket.teams.add(self.team)

        self.sender_email = EmailAddress.objects.create(email_address=self._sender_email)
        self.sender = Person.objects.create(
            first_name='sender_first_name',
            last_name='sender_last_name'
        )
        self.sender.email_addresses.add(self.sender_email)

        self.recipient_email = EmailAddress.objects.create(email_address=self._recipient_email)
        self.recipient = Person.objects.create(
            first_name='recipient_first_name',
            last_name='recipient_last_name',
        )
        self.recipient.email_addresses.add(self.recipient_email)

        cc_people, cc_emails = list(), list()
        for addr in self._cc_emails:
            email = EmailAddress.objects.create(email_address=addr)
            person = Person.objects.create(
                first_name='{}_first_name'.format(addr.split('@')[0]),
                last_name='{}_last_name'.format(addr.split('@')[0])
            )
            person.email_addresses.add(email)
            cc_emails.append(email)
            cc_people.append(person)

        self.cc_emails = cc_emails
        self.cc_people = cc_people

        email_message = EmailMultiAlternatives()
        email_message.body = 'Test message testing 123'
        email_message.from_email = self._sender_email
        email_message.to = self._recipient_email,
        email_message.cc = self._cc_emails
        email_message.subject = 'test message subject'
        email_message.extra_headers['Message-Id'] = 'unique_id_goes_here'
        self.email_message_no_hashid_plain = copy.deepcopy(email_message)

        email_message.attach_alternative(
            '<html><body><p>Test message testing 123</p></body></html>',
            'text/html'
        )
        self.email_message_no_hashid = email_message

    def tearDown(self):
        self.maildir.clear()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(MAILDIR_PATH):
            shutil.rmtree(MAILDIR_PATH)
        super(TestServiceEmailTasks, cls).tearDownClass()

    def test_update_ticket_message_with_valid_hashid(self):
        initial_update_count = self.ticket.updates.count()
        TicketSubscriber.objects.create(
            email_address=self.sender.email_addresses.first(),
            ticket=self.ticket,
            can_view=True,
            can_update=True
        )
        message = copy.deepcopy(self.email_message_no_hashid)
        message.body = 'testing message with valid hashid'
        message.subject = '{} testing one two three'.format(self.ticket.ticket_id)
        message.extra_headers['Message-Id'] = 'new_message_ID_here'
        print(message.message().as_string())
        self.maildir.add(message.message().as_string())
        service.tasks.update_ticket_from_email_message.delay(self.mailbox.get_new_mail()[0].pk, self.ticket.ticket_for_url)
        self.assertEqual(self.ticket.updates.count(), initial_update_count + 1)
        self.assertEqual(self.ticket.updates.order_by('-created_at').first().message_id, message.extra_headers['Message-Id'])

    def test_create_ticket_from_multipart_email(self):
        self.maildir.add(self.email_message_no_hashid.message().as_string())
        msg = self.mailbox.get_new_mail()[0]

        service.tasks.create_ticket_from_email_message(msg.pk)

        ticket = Ticket.objects.filter(message_id=msg.message_id).first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.title, msg.subject)
        self.assertEqual(ticket.created_by, self.sender)
        self.assertIn(self.team, ticket.teams.all())

    def test_create_ticket_from_plain_email(self):
        self.maildir.add(self.email_message_no_hashid_plain.message().as_string())
        msg = self.mailbox.get_new_mail()[0]

        service.tasks.create_ticket_from_email_message(msg.pk)

        ticket = Ticket.objects.filter(message_id=msg.message_id).first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.title, msg.subject)
        self.assertEqual(ticket.created_by, self.sender)

    def test_create_ticket_from_unknown_email_address_known_domain(self):
        message = copy.deepcopy(self.email_message_no_hashid)
        message.from_email = 'unknown_email_address@known_domain.org'
        org = Organization.objects.create(name='Some Organization')
        EmailDomain.objects.create(organization=org, domain_name='known_domain.org')

        self.maildir.add(message.message().as_string())
        msg = self.mailbox.get_new_mail()[0]

        service.tasks.create_ticket_from_email_message(msg.pk)

        ticket = Ticket.objects.get(message_id=msg.message_id)
        self.assertEqual(ticket.organization, org)

    def test_create_ticket_from_unknown_email_address_unknown_domain(self):
        message = copy.deepcopy(self.email_message_no_hashid)
        message.from_email = 'unkown_mailbox@unknown_domain.org'

        self.maildir.add(message.message().as_string())
        msg = self.mailbox.get_new_mail()[0]

        service.tasks.create_ticket_from_email_message(msg.pk)

        ticket = Ticket.objects.get(message_id=msg.message_id)
        self.assertIsNone(ticket.created_by)
        self.assertIsNone(ticket.organization)

    def test_get_cc_addresses(self):
        self.maildir.add(self.email_message_no_hashid.message().as_string())

        msg = self.mailbox.get_new_mail()[0]

        self.assertListEqual(service.tasks.get_cc_addresses(msg), self._cc_emails)

    def test_subscribers_specified_in_message(self):
        self.maildir.add(self.email_message_no_hashid.message().as_string())
        msg = self.mailbox.get_new_mail()[0]

        expected_emails = [self.sender_email] + self.cc_emails

        subscriber_emails = service.tasks.subscribers_specified_in_message(msg)

        self.assertQuerysetEqual(
            subscriber_emails,
            expected_emails,
            transform=lambda obj: obj,
            ordered=False
        )


class TestUpdateViewSet(VerifiedForcedAuthenticationMixin, APITestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='badpassword',
            email='superuser@example.org'
        )
        Person.objects.create(
            first_name='Super',
            last_name='User',
            user=self.superuser
        )
        self.ticket = Ticket.objects.create(
            title='Test ticket',
            organization=Organization.objects.create(name='Example Corp'),
            priority=5,
            created_by=self.superuser.person
        )
        self.client.defaults['HTTP_ACCEPT'] = 'application/vnd.api+json'

    def test_can_edit_update_object_within_time_limit(self):
        self.force_auth(self.superuser)
        url = reverse('ticket-detail', args=[self.ticket.id])
        data = {'data': {
            'type': format_relation_name('Ticket'),
            'id': self.ticket.id,
            'attributes': {
                'priority': 3
            }
        }}
        response = self.client.patch(url, json.dumps(data), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200, response.content.decode())
        response_json_data = json.loads(response.rendered_content.decode())
        print(response.content.decode())
        update_id = response_json_data['data']['relationships']['updates']['data'][0]['id']

        url = reverse('update-detail', args=[update_id])
        data = {'data': {
            'type': format_relation_name('Update'),
            'id': update_id,
            'attributes': {
                'body': "Test comment on changes"
            }
        }}
        response = self.client.patch(url, json.dumps(data), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200, response.content.decode())

    def test_cannot_edit_update_object_after_time_limit(self):
        allowed_delay = settings.TICKET_UPDATE_ALLOW_EDIT_DURATION

        def fake_now():
            return datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(seconds=allowed_delay + 1)

        self.force_auth(self.superuser)
        url = reverse('ticket-detail', args=[self.ticket.id])
        data = {'data': {
            'type': format_relation_name('Ticket'),
            'id': self.ticket.id,
            'attributes': {
                'priority': 3
            }
        }}
        with mock.patch('service.models.update.timezone.now', fake_now):
            # create Update object whose created_by is in the past
            response = self.client.patch(url, json.dumps(data), content_type='application/vnd.api+json')

        self.assertEqual(response.status_code, 200, response.content.decode())
        response_json_data = json.loads(response.content.decode())
        update_id = response_json_data['data']['relationships']['updates']['data'][0]['id']

        url = reverse('update-detail', args=[update_id])
        data = {'data': {
            'type': format_relation_name('Update'),
            'id': update_id,
            'attributes': {
                'body': "Test comment on changes"
            }
        }}
        response = self.client.patch(url, json.dumps(data), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 403, response.content.decode())


class TestDirectlyCloseTicket(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_person', email='test_person@example.org')
        self.person = Person.objects.create(
            first_name='test',
            last_name='person',
            user=self.user
        )
        self.ticket = Ticket.objects.create(
            title='test ticket',
            signaled_by=self.person,
            priority=5
        )

    def test_must_be_ticket_signaler(self):
        another_user = User.objects.create(username='another_user', email='another_user@example.org')
        Person.objects.create(first_name='another', last_name='person', user=another_user)
        self.client.force_authenticate(another_user)
        response = self.client.post('/api/service/tickets/{pk}/close'.format(pk=self.ticket.pk))
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertFalse(self.ticket.is_closed())

    def test_ticket_must_not_be_already_closed(self):
        self.ticket.close_by_signaler()  # force close it for the test
        self.ticket.save()
        self.client.force_authenticate(self.user)
        response = self.client.post('/api/service/tickets/{pk}/close'.format(pk=self.ticket.pk))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content.decode())
        self.assertIn("This ticket is already closed.", response.data['non_field_errors'], response.content.decode())

    def test_close_ticket(self):
        comment = 'test closing a ticket'
        self.client.force_authenticate(self.user)
        response = self.client.post(
            '/api/service/tickets/{pk}/close'.format(pk=self.ticket.pk),
            data={'comment': comment}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.ticket = Ticket.objects.get(pk=self.ticket.pk)  # fsm field prevents refresh_from_db
        self.assertTrue(self.ticket.is_closed())

        latest_update = self.ticket.updates.order_by('created_at').first()
        self.assertEqual(latest_update.body, comment)


class NoteTests(VerifiedForcedAuthenticationMixin, APITestCase):

    def setUp(self):
        self.person = Person.objects.create(
            first_name='example',
            last_name='person'
        )
        email_address = self.person.add_email_address('example_person@example.org')
        self.person.set_primary_email(email_address)
        self.user = self.person.create_login(username='example_person')
        self.user.is_superuser = True
        self.user.save()

        ticket = Ticket.objects.create(
            title='example ticket',
            description='this is a test',
            priority=3
        )
        self.update = Update.objects.create(
            ticket=ticket,
            body='This is an update'
        )

    def test_create_note(self):
        self.force_auth(self.user, verified=True)
        data = {
            "data": {
                "type": "note",
                "attributes": {
                    "body": "testing one two three note"
                },
                "relationships": {
                    "update": {
                        "data": {
                            "type": "update",
                            "id": str(self.update.id)
                        }
                    }
                }
            }
        }
        response = self.client.post(
            '/api/service/notes',
            json.dumps(data),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
