from base64 import b32encode
from binascii import unhexlify
from calendar import timegm
from datetime import datetime, timedelta
from time import time

import django_otp
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django_otp.models import Device
from django_otp.oath import totp
from django_otp.plugins.otp_static.models import StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import exceptions
from rest_framework.compat import unicode_to_repr
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler, JSONWebTokenSerializer, \
    VerificationBaseSerializer
from rest_framework_jwt.settings import api_settings

from noss import tasks
from noss.api.utils import totp_digits, get_otpauth_url
from noss.settings import app_settings
from rest_framework_json_api import serializers, relations


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        # extra_kwargs = {'password': {'write_only': True}}
        exclude = ['password']


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(label=_('Password'))


class ChangePasswordSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordSerializer, self).__init__(*args, **kwargs)
        if not django_otp.user_has_device(self.context['user']):
            self.fields.pop('otp_token')

    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    otp_token = serializers.CharField(default='')

    def validate_old_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError(_("Incorrect password"))
        return value

    def validate_otp_token(self, value):
        user = self.context['user']
        if not django_otp.match_token(user, value):
            raise exceptions.AuthenticationFailed(_("You must provide a valid otp token when changing your password"))
        return value


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'members', 'permissions',)

    members = relations.ResourceRelatedField(
        source='user_set',
        many=True,
        queryset=User.objects
    )

    permissions = relations.ResourceRelatedField(
        queryset=Permission.objects.all,
        many=True
    )


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission
        exclude = ('content_type',)


class TOTPDeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TOTPDevice
        fields = ('id', 'otpauth_url', 'name', 'confirmed',)
        extra_kwargs = {'confirmed': {'read_only': True, 'default': False}}

    def __init__(self, *args, **kwargs):
        super(TOTPDeviceSerializer, self).__init__(*args, **kwargs)
        request = self.context['request']
        if not request.method == 'POST':
            self.fields.pop('otpauth_url', None)

    otpauth_url = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_otpauth_url(obj):
        rawkey = unhexlify(obj.key.encode('ascii'))
        b32key = b32encode(rawkey).decode('utf-8')
        return get_otpauth_url(obj.user.username, b32key, issuer="ZEROFAIL", digits=obj.digits)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        return TOTPDevice.objects.create(**validated_data)

    def save(self, **kwargs):
        # refresh from db to work around issues caused by cached bytestring value for instance.key
        instance = super(TOTPDeviceSerializer, self).save(**kwargs)
        instance.refresh_from_db()
        return instance


class StaticTokenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StaticToken
        fields = ('token',)


class TOTPTokenSerializer(serializers.Serializer):
    token = serializers.IntegerField()

    def __init__(self, device, user, metadata=None, **kwargs):
        super(TOTPTokenSerializer, self).__init__(**kwargs)
        self.key = device.key
        self.tolerance = 1
        self.t0 = 0
        self.step = 30
        self.drift = 0
        self.digits = totp_digits()
        self.user = user
        self.metadata = metadata or {}

    @property
    def bin_key(self):
        """
        The secret key as a binary string.
        """
        return unhexlify(self.key.encode())

    def validate_token(self, value):
        token = value
        validated = False
        t0s = [self.t0]
        key = self.bin_key
        if 'valid_t0' in self.metadata:
            t0s.append(int(time()) - self.metadata['valid_t0'])
        for t0 in t0s:
            for offset in range(-self.tolerance, self.tolerance):
                if totp(key, self.step, t0, self.digits, self.drift + offset) == token:
                    self.drift = offset
                    self.metadata['valid_t0'] = int(time()) - t0
                    validated = True
        if not validated:
            raise serializers.ValidationError(_('Entered token is not valid.'))
        return token


class OTPJSONWebTokenAuthenticationSerializer(JSONWebTokenSerializer):
    """
    Serializer class used to validate a username, password and token.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    otp_token = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                # Include original issued at time for a brand new token,
                # to allow token refresh
                if api_settings.JWT_ALLOW_REFRESH:
                    payload['orig_iat'] = timegm(
                        datetime.utcnow().utctimetuple()
                    )

                if attrs.get('otp_token') and django_otp.user_has_device(user):
                    device = django_otp.match_token(user, attrs.get('otp_token'))
                    if device:
                        payload['otp_device_id'] = device.persistent_id
                    else:
                        msg = _('Unable to validate the provided token.')
                        raise serializers.ValidationError(msg)

                if (not django_otp.user_has_device(user) or
                        payload.get('otp_device_id', False) or
                        app_settings.ALLOW_UNVERIFIED_STAFF):
                    queue_name = 'ws.' + payload[settings.JWT_PAYLOAD_WSID_KEY]
                    kwargs = {
                        'queue': queue_name,
                        'durable': True,
                        'auto_delete': True,
                        'arguments': {"x-expires": int(api_settings.JWT_EXPIRATION_DELTA.total_seconds())}}
                    tasks.amqp_queue_declare.delay(kwargs)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to login with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class RefreshJWTSerializer(VerificationBaseSerializer):
    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')

        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _('Refresh has expired.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('orig_iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_payload['orig_iat'] = orig_iat

        new_payload = update_with_verified_status(user, payload, new_payload)

        return {
            'token': jwt_encode_handler(new_payload),
            'user': user
        }


def update_with_verified_status(user, old_payload, new_payload):
    if 'otp_device_id' in old_payload:
        device = Device.from_persistent_id(old_payload['otp_device_id'])
        if device is not None and device.user_id == user.id:
            new_payload['otp_device_id'] = device.persistent_id
    return new_payload


class HyperlinkedVersionableModelSerializer(serializers.HyperlinkedModelSerializer):
    identity = serializers.CharField(read_only=True)
    version_start_date = serializers.DateTimeField(read_only=True)
    version_end_date = serializers.DateTimeField(read_only=True)
    version_birth_date = serializers.DateTimeField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        new_instance_version = instance.clone()
        for attr, value in validated_data.items():
            setattr(new_instance_version, attr, value)
        new_instance_version.save()

        return new_instance_version


class CurrentPersonDefault(object):
    def set_context(self, serializer_field):
        self.user = serializer_field.context['request'].user

    def __call__(self):
        return self.user.person

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)