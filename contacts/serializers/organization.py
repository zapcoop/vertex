from contacts.models import Organization, Person
from contacts.serializers.person import PersonSerializer
from contacts.serializers.organizationdepartment import OrganizationDepartmentSerializer
from contacts.serializers.emaildomain import EmailDomainSerializer
from contacts.serializers.phonenumber import PhoneNumberSerializer
from contacts.serializers.emailaddress import EmailAddressSerializer
from contacts.serializers.url import URLSerializer
from noss.api.fields import PermissionsField
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api import serializers
from tags.serializers import TagSerializer
from tags.models import Tag

__author__ = 'jsenecal'


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        # depth = 1

    included_serializers = {
        'children': 'self',
        'parent': 'self',
        'resellers': 'self',
        'customers': 'self',
        'departments': OrganizationDepartmentSerializer,
        'people': PersonSerializer,
        'administrators': PersonSerializer,
        'email_domains': EmailDomainSerializer,
        'phone_numbers': PhoneNumberSerializer,
        'email_addresses': EmailAddressSerializer,
        'urls': URLSerializer,
        'tags': TagSerializer
    }

    permissions = PermissionsField()

    children = ResourceRelatedField(
        related_link_view_name='organization-children-list',
        related_link_url_kwarg='parent_pk',
        self_link_view_name='organization-relationships',
        queryset=Organization.objects,
        many=True,
        required=False
    )
    parent = ResourceRelatedField(
        related_link_view_name='organization-parent',
        self_link_view_name='organization-relationships',
        read_only=True,
        required=False
    )
    resellers = ResourceRelatedField(
        related_link_view_name='organization-resellers-list',
        related_link_url_kwarg='customer_pk',
        self_link_view_name='organization-relationships',
        queryset=Organization.objects,
        many=True,
        required=False
    )
    customers = ResourceRelatedField(
        related_link_view_name='organization-customers-list',
        related_link_url_kwarg='reseller_pk',
        self_link_view_name='organization-relationships',
        queryset=Organization.objects,
        many=True,
        required=False
    )
    departments = ResourceRelatedField(
        related_link_view_name='organization-departments-list',
        related_link_url_kwarg='organization_pk',
        self_link_view_name='organization-relationships',
        read_only=True,
        many=True,
        required=False
    )
    people = ResourceRelatedField(
        related_link_view_name='organization-people-list',
        related_link_url_kwarg='organization_pk',
        self_link_view_name='organization-relationships',
        queryset=Person.objects,
        many=True,
        required=False
    )
    administrators = ResourceRelatedField(
        related_link_view_name='organization-administrators-list',
        related_link_url_kwarg='managed_organization_pk',
        self_link_view_name='organization-relationships',
        queryset=Person.objects,
        many=True,
        required=False
    )
    email_domains = ResourceRelatedField(
        related_link_view_name='organization-emaildomains-list',
        related_link_url_kwarg='organization_pk',
        self_link_view_name='organization-relationships',
        read_only=True,
        many=True,
        required=False
    )
    phone_numbers = ResourceRelatedField(
        related_link_view_name='organization-phonenumbers-list',
        related_link_url_kwarg='organization_pk',
        self_link_view_name='organization-relationships',
        read_only=True,
        many=True,
        required=False
    )
    email_addresses = ResourceRelatedField(
        related_link_view_name='organization-emailaddresses-list',
        related_link_url_kwarg='organization_pk',
        self_link_view_name='organization-relationships',
        read_only=True,
        many=True,
        required=False
    )
    urls = ResourceRelatedField(
        related_link_view_name='organization-urls-list',
        related_link_url_kwarg='organization_pk',
        self_link_view_name='organization-relationships',
        read_only=True,
        many=True,
        required=False
    )
    tags = ResourceRelatedField(
        read_only=True,
        many=True,
        required=False
    )

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        request = context.get('request') if context else None

        # Remove 'notes' field if request user is not staff
        if request and not request.user.is_staff:
            self.fields.pop('notes')
        super(OrganizationSerializer, self).__init__(*args, **kwargs)
