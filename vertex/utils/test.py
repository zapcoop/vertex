import requests
from rest_framework.test import APILiveServerTestCase


class PaginatedAPITestMixin(object):
    def get_count_or_fail(self, data):
        try:
            return data['meta']['pagination']['count']
        except KeyError:
            self.fail("Couldn't get 'count' from response: \n{!r}".format(data))
        except TypeError:
            self.fail("Response data is not a dict: \n{!r}".format(data))


class JWTAuthenticatedLiveServerTestCase(APILiveServerTestCase):
    def get_new_jwt(self, username, password):
        response = self.client.post(
            '/api-auth',
            {
                'username': username,
                'password': password
            }
        )
        return response.data['token']


class VerifiedForcedAuthenticationMixin(object):

    def force_auth(self, user, verified=True):
        user.is_verified = verified
        self.client.force_authenticate(user)
