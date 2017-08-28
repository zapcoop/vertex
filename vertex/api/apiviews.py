import re
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework import status
from rest_framework import exceptions
from contacts.models import Person
from contacts.serializers import CurrentPersonSerializer
from rest_framework_json_api.utils import format_relation_name

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from noss.api.serializers import (OTPJSONWebTokenAuthenticationSerializer,
                                  ChangePasswordSerializer, RefreshJWTSerializer)
from contacts.serializers.person import SetPrimaryEmailSerializer

AUTH_HEADER_PATTERN = re.compile(
    r'^' + settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX'] + r'\s+(?P<token>\S+)$',
    flags=re.IGNORECASE
)


class CurrentUserView(GenericAPIView):
    """
    View to display the current logged-in user information.

    * Only authenticated users are able to access this view.

    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Person.objects
    serializer_class = CurrentPersonSerializer

    def get_object(self):
        return self.request.user.person

    def get(self, request, *args, **kwargs):
        """
        Returns the serialized current user object.
        """
        person = self.get_object()
        serializer = self.get_serializer(person)
        return Response(serializer.data)


class CurrentUserPasswordChangeView(APIView):
    """View to change the currently authenticated user's password."""
    permission_classes = (permissions.IsAuthenticated,)
    resource_name = format_relation_name('User')

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"status": _("password changed")})


class CurrentUserSetPrimaryEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    resource_name = format_relation_name('EmailAddress')

    def post(self, request, *args, **kwargs):
        # add 'type' back to data. The parser strips it but ResourceIDSerializer expects it to be there.
        # this should be safe because the parser will cause an error if the type doesn't match
        request.data.update(type=self.resource_name)

        person = request.user.person
        serializer = SetPrimaryEmailSerializer(data=request.data, person=person)
        serializer.is_valid(raise_exception=True)
        person.set_primary_email(serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ObtainJSONWebTokenView(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = OTPJSONWebTokenAuthenticationSerializer
    resource_name = 'api_auth'


class RefreshJSONWebTokenView(JSONWebTokenAPIView):
    serializer_class = RefreshJWTSerializer
    resource_name = 'api_auth'

    def get_serializer(self, *args, **kwargs):
        token_from_header = self._get_token_from_header()
        if token_from_header:
            if 'data' in kwargs:
                kwargs['data'] = dict(kwargs['data']) # need to convert immutable QueryDict into mutable dict
            else:
                kwargs['data'] = dict()
            if 'token' in kwargs['data']:
                raise exceptions.ValidationError(_('You have tried to refresh a token in the request body'
                                                ' while also setting a token in the AUTHORIZATION header.'
                                                ' This is unsupported due to ambiguity.'))
            kwargs['data']['token'] = token_from_header
        return super(RefreshJSONWebTokenView, self).get_serializer(*args, **kwargs)

    def _get_token_from_header(self):
        if 'HTTP_AUTHORIZATION' in self.request.META:
            match = AUTH_HEADER_PATTERN.match(self.request.META['HTTP_AUTHORIZATION'])
            if match:
                return match.group('token')
            else:
                return None
