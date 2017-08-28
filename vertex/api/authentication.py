import jwt
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, jwt_decode_handler


class OTPJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.
        Otherwise returns `None`.

        Most of the time the user returned will be the one from the request
        as this user object is populated with the appropriate otp fields and helper methods.

        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        payload_user = self.authenticate_credentials(payload)
        request = request._request
        request_user = getattr(request, 'user', None)

        if request_user is None or request_user.pk != payload_user.pk:
            return payload_user, jwt_value
        else:
            return request_user, jwt_value