import graphene

from graphene_django.types import DjangoObjectType

from contacts.models import (
    ContactGroup,
    OrganizationDepartment,
    EmailAddress,
    PhoneNumber,
    URL,
    Organization,
    OrganizationAlias,
    Person
)


class ContactGroupType(DjangoObjectType):
    class Meta:
        model = ContactGroup


class OrganizationDepartmentType(DjangoObjectType):
    class Meta:
        model = OrganizationDepartment


class EmailAddressType(DjangoObjectType):
    class Meta:
        model = EmailAddress


class PhoneNumberType(DjangoObjectType):
    class Meta:
        model = PhoneNumber


class URLType(DjangoObjectType):
    class Meta:
        model = URL


class OrganizationType(DjangoObjectType):
    people = graphene.List("contacts.schema.PersonType")
    administrators = graphene.List("contacts.schema.PersonType")

    def resolve_people(self, args, context, info):
        return self.people.all()

    def resolve_administrators(self, args, context, info):
        return self.people.all()

    class Meta:
        model = Organization


class OrganizationAliasType(DjangoObjectType):
    class Meta:
        model = OrganizationAlias


class PersonType(DjangoObjectType):
    class Meta:
        model = Person


class Query(graphene.AbstractType):
    contact_group = graphene.Field(
        ContactGroupType,
        id=graphene.Int()
    )
    all_contact_groups = graphene.List(ContactGroupType)

    organization = graphene.Field(
        OrganizationType,
        id=graphene.Int()
    )
    all_organizations = graphene.List(OrganizationType)

    person = graphene.Field(
        PersonType,
        id=graphene.Int()
    )
    all_people = graphene.List(PersonType)

    def resolve_contact_group(self, args, context, info):
        id = args.get('id')

        if id is not None:
            return ContactGroup.objects.get(pk=id)

        return None

    def resolve_all_contact_groups(self, args, context, info):
        return ContactGroup.objects.prefetch_related('people', 'organizations').all()

    def resolve_organization(self, args, context, info):
        id = args.get('id')

        if id is not None:
            return Organization.objects.get(pk=id)

        return None

    def resolve_all_organizations(self, args, context, info):
        return Organization.objects.all()

    def resolve_person(self, args, context, info):
        id = args.get('id')

        if id is not None:
            return Person.objects.get(pk=id)

        return None

    def resolve_all_people(self, args, context, info):
        return Person.objects.all()
