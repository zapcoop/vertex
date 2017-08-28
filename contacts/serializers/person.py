import re
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
import django_otp
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from contacts.models import Person, Organization, OrganizationDepartment, EmailAddress
from contacts.serializers.emailaddress import EmailAddressSerializer
from contacts.serializers.phonenumber import PhoneNumberSerializer
from contacts.serializers.url import URLSerializer
from noss.api.serializermixins import FilterRelatedMixin
from noss.info import Info

__author__ = 'jsenecal'

User = get_user_model()


class PersonSerializer(FilterRelatedMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person

    def __init__(self, *args, **kwargs):
        super(PersonSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and getattr(getattr(request, 'user'), 'is_superuser', False):
            self.fields['is_superuser'] = serializers.BooleanField(read_only=True)

    included_serializers = {
        'phone_numbers': PhoneNumberSerializer,
        'email_addresses': EmailAddressSerializer,
        'urls': URLSerializer,
        'assigned_tickets': 'service.serializers.TicketSerializer',
        'created_tickets': 'service.serializers.TicketSerializer',
        'originated_tickets': 'service.serializers.TicketSerializer',
        'departments': 'contacts.serializers.OrganizationDepartmentSerializer',
        'managed_departments': 'contacts.serializers.OrganizationDepartmentSerializer',
        'organizations': 'contacts.serializers.OrganizationSerializer',
        'managed_organizations': 'contacts.serializers.OrganizationSerializer'
    }

    full_name = serializers.ReadOnlyField()

    phone_numbers = ResourceRelatedField(
        related_link_view_name='person-phonenumbers-list',
        related_link_url_kwarg='person_pk',
        self_link_view_name='person-relationships',
        read_only=True,
        many=True,
        required=False
    )
    email_addresses = ResourceRelatedField(
        related_link_view_name='person-emailaddresses-list',
        related_link_url_kwarg='person_pk',
        self_link_view_name='person-relationships',
        read_only=True,
        many=True,
        required=False
    )
    urls = ResourceRelatedField(
        related_link_view_name='person-urls-list',
        related_link_url_kwarg='person_pk',
        self_link_view_name='person-relationships',
        read_only=True,
        many=True,
        required=False
    )
    departments = ResourceRelatedField(
        related_link_view_name='person-departments-list',
        related_link_url_kwarg='person_pk',
        self_link_view_name='person-relationships',
        queryset=OrganizationDepartment.objects,
        many=True,
        required=False
    )
    managed_departments = ResourceRelatedField(
        related_link_view_name='person-manageddepartments-list',
        related_link_url_kwarg='manager_pk',
        self_link_view_name='person-relationships',
        queryset=OrganizationDepartment.objects,
        many=True,
        required=False
    )
    organizations = ResourceRelatedField(
        related_link_view_name='person-organizations-list',
        related_link_url_kwarg='person_pk',
        self_link_view_name='person-relationships',
        queryset=Organization.objects,
        many=True,
        required=False
    )
    managed_organizations = ResourceRelatedField(
        related_link_view_name='person-managedorganizations-list',
        related_link_url_kwarg='manager_pk',
        self_link_view_name='person-relationships',
        queryset=Organization.objects,
        many=True,
        required=False
    )

    username = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    gravatar_url = serializers.URLField(read_only=True)

    def filter_organizations(self, qs):
        try:
            request = self.context['request']
        except KeyError:
            return qs
        else:
            if request.user.is_staff:
                return qs
            else:
                return request.user.person.managed_organizations

    def filter_groups(self, qs):
        try:
            request = self.context['request']
        except KeyError:
            return qs
        else:
            if request.user.is_staff:
                return qs
            else:
                return request.user.person.groups


class CreateLoginSerializer(serializers.Serializer):
    """Create a login account (User object) for an existing Person. Note: Should be used within a transaction,
    otherwise extraneous EmailAddress objects could be created."""
    username = serializers.CharField(max_length=30, )
    is_superuser = serializers.BooleanField(required=False, default=False)
    is_staff = serializers.BooleanField(required=False, default=False)

    def __init__(self, *args, **kwargs):
        super(CreateLoginSerializer, self).__init__(*args, **kwargs)
        self.user = self.context['request'].user
        self.person = self.context['person']

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'This value may contain only letters, numbers and @/./+/-/_ characters.'
            )
        return value

    def validate_is_superuser(self, value):
        if value and not self.user.is_superuser:
            raise exceptions.PermissionDenied("You don't have permission to create superusers.")
        return value

    def validate_is_staff(self, value):
        if value and not self.user.is_superuser:
            raise exceptions.PermissionDenied("You don't have permission to create staff users.")
        return value

    def validate(self, attrs):
        if self.person.user:
            raise serializers.ValidationError("A login account already exists for this Person")
        tmp = User(**attrs)
        tmp.clean()
        tmp.validate_unique()
        return attrs

    def create(self, validated_data):
        return self.person.create_login(**validated_data)


class CurrentPersonSerializer(PersonSerializer):
    def __init__(self, *args, **kwargs):
        super(CurrentPersonSerializer, self).__init__(*args, **kwargs)
        self.user = self.context['request'].user  # request.user has the is_verified method

    is_verified = serializers.SerializerMethodField('check_if_verified')
    has_otp_device = serializers.SerializerMethodField('user_has_device')
    apps = serializers.SerializerMethodField('get_apps_info')
    last_login = serializers.DateTimeField(source='user.last_login')
    is_staff = serializers.BooleanField(source='user.is_staff')
    is_superuser = serializers.BooleanField(source='user.is_superuser')

    def check_if_verified(self, instance):
        if hasattr(self.user, 'is_verified'):
            return self.user.is_verified()
        else:
            return False

    def user_has_device(self, instance):
        return django_otp.user_has_device(self.user)

    def get_apps_info(self, instance):
        return Info.get_dict(self.user, 'apps')


class SetPrimaryEmailSerializer(serializers.ResourceIdentifierObjectSerializer):
    model_class = EmailAddress

    def __init__(self, *args, **kwargs):
        self.person = kwargs.pop('person', None)
        super(SetPrimaryEmailSerializer, self).__init__(*args, **kwargs)
        self.validators.append(self.validate_email_belongs_to_person)

    def validate_email_belongs_to_person(self, email_address):
        if email_address.person and email_address.person == self.person:
            return email_address
        raise serializers.ValidationError(_("Invalid email address"))