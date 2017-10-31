import graphene
from graphene_django.filter import DjangoFilterConnectionField

from graphene_django.types import DjangoObjectType

from contacts.models import (ContactGroup,
                             OrganizationDepartment,
                             EmailAddress,
                             PhoneNumber,
                             URL,
                             Organization,
                             OrganizationAlias,
                             Person,
                             PeopleOrganizations)


class ContactGroupNode(DjangoObjectType):
    class Meta:
        model = ContactGroup
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'people': ['exact'],
            'people__first_name': ['exact', 'icontains', 'istartswith'],
            'people__last_name': ['exact', 'icontains', 'istartswith'],
            'organizations': ['exact'],
            'organizations__name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)


class OrganizationDepartmentNode(DjangoObjectType):
    class Meta:
        model = OrganizationDepartment
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'people': ['exact'],
            'organization': ['exact'],
            'organization__name': ['exact', 'icontains', 'istartswith'],
            'people__first_name': ['exact', 'icontains', 'istartswith'],
            'people__last_name': ['exact', 'icontains', 'istartswith'],
            'managers__first_name': ['exact', 'icontains', 'istartswith'],
            'managers__last_name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)


class EmailAddressNode(DjangoObjectType):
    class Meta:
        model = EmailAddress
        filter_fields = {
            'email_address': ['exact', 'icontains', 'istartswith'],
            'information_type': ['exact'],
            'person': ['exact'],
            'organization': ['exact'],
            'organization__name': ['exact', 'icontains', 'istartswith'],
            'person__first_name': ['exact', 'icontains', 'istartswith'],
            'person__last_name': ['exact', 'icontains', 'istartswith'],
            'primary': ['exact'],
        }
        interfaces = (graphene.relay.Node,)


class PhoneNumberNode(DjangoObjectType):
    class Meta:
        model = PhoneNumber
        filter_fields = {
            'phone_number': ['exact', 'icontains', 'istartswith'],
            'information_type': ['exact'],
            'person': ['exact'],
            'organization': ['exact'],
            'organization__name': ['exact', 'icontains', 'istartswith'],
            'person__first_name': ['exact', 'icontains', 'istartswith'],
            'person__last_name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)


class URLNode(DjangoObjectType):
    class Meta:
        model = URL
        filter_fields = {
            'url': ['exact', 'icontains', 'istartswith'],
            'information_type': ['exact'],
            'person': ['exact'],
            'organization': ['exact'],
            'organization__name': ['exact', 'icontains', 'istartswith'],
            'person__first_name': ['exact', 'icontains', 'istartswith'],
            'person__last_name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)


class PeopleOrganizationsNode(DjangoObjectType):
    class Meta:
        model = PeopleOrganizations
        filter_fields = {
            'person': ['exact'],
            'organization': ['exact'],
            'organization__name': ['exact', 'icontains', 'istartswith'],
            'person__first_name': ['exact', 'icontains', 'istartswith'],
            'person__last_name': ['exact', 'icontains', 'istartswith'],
            'role': ['exact', 'icontains', 'istartswith'],

        }
        interfaces = (graphene.relay.Node,)


class OrganizationNode(DjangoObjectType):
    people = DjangoFilterConnectionField("contacts.schema.nodes.PersonNode")
    administrators = DjangoFilterConnectionField("contacts.schema.nodes.PersonNode")

    def resolve_people(self, info):
        return self.people.all()

    def resolve_administrators(self, info):
        return self.people.all()

    class Meta:
        model = Organization
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact'],
            'aliases__name': ['exact', 'icontains', 'istartswith'],
            # 'people': ['exact'],
            'administrators': ['exact'],
            # 'people__first_name': ['exact', 'icontains', 'istartswith'],
            # 'people__last_name': ['exact', 'icontains', 'istartswith'],
            'administrators__first_name': ['exact', 'icontains', 'istartswith'],
            'administrators__last_name': ['exact', 'icontains', 'istartswith'],
            'notes': ['icontains'],
        }
        interfaces = (graphene.relay.Node,)


class OrganizationAliasNode(DjangoObjectType):
    class Meta:
        model = OrganizationAlias
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)


class PersonNode(DjangoObjectType):
    organizations = graphene.relay.ConnectionField("contacts.schema.connections.PeopleOrganizationsConnection")

    class Meta:
        model = Person
        filter_fields = {
            'first_name': ['exact', 'icontains', 'istartswith'],
            'middle_name': ['exact', 'icontains', 'istartswith'],
            'last_name': ['exact', 'icontains', 'istartswith'],
            'slug': ['exact'],
            'gender': ['exact'],
            'notes': ['icontains'],
            'user__username': ['exact', 'icontains'],
            'user__is_staff': ['exact', ],
            'user__is_superuser': ['exact', ],
        }
        interfaces = (graphene.relay.Node,)
