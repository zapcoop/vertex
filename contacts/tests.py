import json

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APITestCase

from rest_framework import status

from rest_framework_json_api.utils import format_relation_name
from noss.utils.test import VerifiedForcedAuthenticationMixin, PaginatedAPITestMixin
from .models import Person, EmailAddress


class PersonTests(TestCase):
    def test_changing_name_updates_corresponding_user_object_if_exists(self):
        person = Person.objects.create(
            first_name='Jane',
            last_name='Doe',
            nickname='jdoe'
        )
        person.user = User.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.org',
            username='jdoe'
        )

        person.last_name = 'Smith'
        person.save()

        self.assertEqual(person.user.last_name, 'Smith')


class PersonAPITests(VerifiedForcedAuthenticationMixin, APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='badpassword',
            email='superuser@example.org'
        )
        Person.objects.create(user=self.superuser)

        self.test_person = Person.objects.create(
            first_name='Example',
            last_name='Person'
        )

        self.username = 'example_user'

    def test_add_login_action(self):
        self.force_auth(self.superuser)
        request_data = {'data': {
            'type': 'action',
            'attributes': {
                'username': self.username,
            }
        }}
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(
            User.objects.filter(username=self.username).exists(),
            'user was not created'
        )

        self.assertEqual(
            User.objects.get(username=self.username).person,
            self.test_person,
            'user created but not associated to person'
        )

    def test_requestor_must_have_adequate_permissions(self):
        staff_user = User.objects.create(username='staff_user', is_staff=True)
        Person.objects.create(user=staff_user, first_name='staff', last_name='user')
        self.force_auth(staff_user)

        request_data = {'data': {
            'type': 'action',
            'attributes': {
                'username': self.username,
            }
        }}
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 403)

    def test_add_login_action_is_staff_flag_forbidden_for_staff_user(self):
        staff_user = User.objects.create(username='staff_user', is_staff=True)
        staff_user.user_permissions.add(*Permission.objects.filter(
            content_type__app_label__in=('auth', 'contacts',)))
        Person.objects.create(user=staff_user, first_name='staff', last_name='user')
        self.force_auth(staff_user)

        request_data = {'data': {
            'type': 'action',
            'attributes': {
                'username': self.username,
                'is_staff': True,
                'is_superuser': True
            }
        }}
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 403, response.content.decode())
        self.assertFalse(User.objects.filter(username=self.username).exists())

        # now make sure that the 403 was due to the is_staff & is_superuser
        request_data['data']['attributes']['is_staff'] = False
        request_data['data']['attributes']['is_superuser'] = False
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200, response.content.decode())
        self.assertTrue(User.objects.filter(username=self.username).exists())

    def test_add_login_action_is_staff_flag_allowed_for_superuser(self):
        self.force_auth(self.superuser)
        request_data = {'data': {
            'type': 'action',
            'attributes': {
                'username': self.username,
                'is_superuser': True
            }
        }}
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(
            User.objects.filter(username=self.username).exists(),
            'user was not created'
        )
        self.assertTrue(User.objects.get(username=self.username).is_superuser)

    def test_cannot_use_action_as_regular_unpriviledged_user(self):
        unprivileged_user = User.objects.create(
            username='unprivileged',
            email='unprivileged@example.org'
        )
        Person.objects.create(user=unprivileged_user, first_name='unprivileged', last_name='user')

        self.force_auth(unprivileged_user, verified=False)
        request_data = {'data': {
            'type': 'action',
            'attributes': {
                'username': self.username,
            }
        }}
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 403)

    def test_can_only_add_one_login_per_user(self):
        self.test_person.user = User.objects.create(username='test_user', email='test_user@example.org')
        self.test_person.save()
        self.force_auth(self.superuser)
        request_data = {'data': {
            'type': 'action',
            'attributes': {
                'username': self.username,
            }
        }}
        response = self.client.post(
            '/api/contacts/people/{}/create_login'.format(self.test_person.id),
            data=json.dumps(request_data),
            content_type='application/vnd.api+json',
            Accept='application/vnd.api+json'
        )

        self.assertEqual(response.status_code, 400, response.content.decode())
        self.assertIn(
            'A login account already exists for this Person',
            response.data.get('non_field_errors')
        )

    def test_set_primary_email(self):
        self.test_person.user = User.objects.create(username=self.username, email='test1@example.org')
        self.test_person.save()
        self.test_person.email_addresses.create(email_address='test1@example.org')
        self.test_person.email_addresses.create(email_address='test2@example.org')

        self.force_auth(self.superuser)
        response = self.client.post(
            '/api/contacts/people/{}/set_primary_email'.format(self.test_person.id),
            data={
                'type': 'email_address',
                'id': str(EmailAddress.objects.get(email_address='test2@example.org').id)
            }
        )
        self.assertEqual(response.status_code, 204, response.content.decode())
        self.assertEqual(
            self.test_person.email_addresses.get(primary=True).email_address,
            'test2@example.org'
        )

        user = self.test_person.user
        user.refresh_from_db()
        self.assertEqual(user.email, 'test2@example.org')


class CurrentPersonEndpointTests(PaginatedAPITestMixin, APITestCase):
    def setUp(self):
        self.current_person_password = 'password'
        self.current_person = Person.objects.create(
            first_name='Current',
            last_name='Person',
        )
        EmailAddress.objects.create(email_address='current_person@example.org', person=self.current_person)
        self.current_person.create_login(
            username='current_person',
            email='current_person@example.org',
            first_name='Current',
            last_name='Person'
        )
        self.current_person.user.set_password(self.current_person_password)
        self.current_person.user.save()
        self.client.defaults['HTTP_ACCEPT'] = 'application/vnd.api+json'

    def test_returns_current_person(self):
        self.authenticate_without_otp()
        response = self.client.get('/api/me')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            get_response_info_string(response)
        )
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['data']['type'], format_relation_name('Person'))
        self.assertEqual(response_data['data']['id'], str(self.current_person.id))

    def test_otp_verified_status(self):
        self.authenticate_without_otp()
        response = self.client.get('/api/me')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            get_response_info_string(response)
        )

        self.assertFalse(response.data['has_otp_device'])

        self.authenticate_with_otp()
        response = self.client.get('/api/me')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            get_response_info_string(response)
        )
        self.assertTrue(response.data['has_otp_device'])
        self.assertTrue(response.data['is_verified'])

    def test_result_has_apps_and_full_name_fields(self):
        self.authenticate_without_otp()
        response = self.client.get('/api/me')
        self.assertIn('apps', response.data, "'apps' field not found in result")
        self.assertIn('full_name', response.data, "'full_name' field not found in result")

    def test_username_fields(self):
        test_user_fields = ('last_login', 'is_superuser', 'is_staff',)
        self.authenticate_without_otp()
        response = self.client.get('/api/me')

        user = self.current_person.user
        for field in test_user_fields:
            self.assertIn(field, response.data, 'Field {} not found in result'.format(field))
            self.assertEqual(
                response.data[field],
                getattr(user, field),
                'Wrong value for field {}; expecting: {}, was: {}'.format(
                    field,
                    getattr(user, field),
                    response.data[field]
                )
            )

    def test_set_primary_email(self):
        new_email = EmailAddress.objects.create(email_address='new_email@example.org')
        self.current_person.email_addresses.add(new_email)
        self.authenticate_without_otp()
        response = self.client.get(
            reverse('person-emailaddresses-list', kwargs={'person_pk': self.current_person.pk})
        )
        self.assertEqual(
            self.get_count_or_fail(response.data),
            2,
            response.data
        )

        response = self.client.post(
            '/api/me/set_primary_email',
            data={
                'type': 'email_address',
                'id': new_email.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, get_response_info_string(response))
        new_email.refresh_from_db()
        self.assertTrue(new_email.primary)

    def authenticate_without_otp(self):
        data = {
            'username': self.current_person.user.username,
            'password': self.current_person_password
        }
        response = self.client.post('/api-auth', data=data)
        self.client.defaults.update({'HTTP_AUTHORIZATION': 'Bearer {}'.format(response.data['token'])})

    def authenticate_with_otp(self):
        totp_device = TOTPDevice.objects.create(name='totp device', user=self.current_person.user)
        totp_device.refresh_from_db()
        totp = TOTP(key=totp_device.bin_key)
        data = {
            'username': self.current_person.user.username,
            'password': self.current_person_password,
            'otp_token': totp.token()
        }
        response = self.client.post('/api-auth', data=data)
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(response.data['token'])


def get_response_info_string(response):
    return 'Status: {}\nContent:\n{}'.format(response.status_code, response.content.decode())
