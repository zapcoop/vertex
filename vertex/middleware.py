from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.models import Device
from django_otp.middleware import IsVerified
import jwt
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework_jwt.authentication import jwt_decode_handler

from noss.api.authentication import OTPJSONWebTokenAuthentication


class JWTOTPAuthenticationMiddleware(object):
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware` and
    performs an analogous function. Just as AuthenticationMiddleware populates
    ``request.user`` based on session data, OTPMiddleware populates
    ``request.user.otp_device`` to the :class:`~django_otp.models.Device`
    object that has verified the user, or ``None`` if the user has not been
    verified.  As a convenience, this also installs ``user.is_verified()``,
    which returns ``True`` if ``user.otp_device`` is not ``None``.
    """

    def process_request(self, request):

        jwt_value = None

        try:
            user_jwt = OTPJSONWebTokenAuthentication().authenticate(Request(request))
        except exceptions.AuthenticationFailed:
            user_jwt = None
        if user_jwt is not None:
            request.user = user_jwt[0]
            jwt_value = user_jwt[1]

        user = getattr(request, 'user', None)

        if user is None:
            return None

        user.otp_device = None
        user.is_verified = IsVerified(user)

        if user.is_anonymous():
            return None

        if jwt_value:
            try:
                payload = jwt_decode_handler(jwt_value)
            except jwt.InvalidTokenError:
                return None
            else:
                device_id = payload.get('otp_device_id')
                user.jwt_payload = payload
        else:
            device_id = request.session.get(DEVICE_ID_SESSION_KEY)

        device = Device.from_persistent_id(device_id) if device_id else None

        if (device is not None) and (device.user_id != user.id):
            device = None

        if (device is None) and (DEVICE_ID_SESSION_KEY in request.session):
            del request.session[DEVICE_ID_SESSION_KEY]

        user.otp_device = device

        return None