import uuid
from datetime import datetime
from urllib.parse import quote, urlencode

import django_otp
from django.conf import settings
from rest_framework_jwt.settings import api_settings

from noss import tasks


def get_otpauth_url(account_name, secret, issuer=None, digits=None):
    # For a complete run-through of all the parameters, have a look at the
    # specs at:
    # https://github.com/google/google-authenticator/wiki/Key-Uri-Format

    # quote and urlencode work best with bytes, not unicode strings.
    account_name = account_name.encode('utf8')
    issuer = issuer.encode('utf8') if issuer else None

    label = quote(b':'.join([issuer, account_name]) if issuer else account_name)

    query = {
        'secret': secret,
        'digits': digits or totp_digits()
    }

    if issuer:
        query['issuer'] = issuer

    return 'otpauth://totp/%s?%s' % (label, urlencode(query))


def totp_digits():
    """
    Returns the number of digits (as configured by the TOTP_DIGITS setting)
    for totp tokens. Defaults to 6
    """
    return getattr(settings, 'TOTP_DIGITS', 6)


def jwt_payload_handler(user):
    websocket_id = (user.jwt_payload.get('settings.JWT_PAYLOAD_WSID_KEY', str(uuid.uuid1()))
                    if hasattr(user, 'jwt_payload')
                    else str(uuid.uuid1()))

    return {
        settings.JWT_PAYLOAD_USERID_KEY: user.pk,
        settings.JWT_PAYLOAD_WSID_KEY: websocket_id,
        'username': user.username,
        'has_otp_device': django_otp.user_has_device(user),
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
    }
