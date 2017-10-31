import graphene

from contacts.schema.nodes import (PersonNode,
                             OrganizationNode,
                             ContactGroupNode,
                             PeopleOrganizationsNode)




class PeopleOrganizationsConnection(graphene.relay.Connection):
    class Meta:
        node = PeopleOrganizationsNode


class PersonConnection(graphene.relay.Connection):
    class Meta:
        node = PersonNode


class OrganizationConnection(graphene.relay.Connection):
    class Meta:
        node = OrganizationNode


class ContactGroupConnection(graphene.relay.Connection):
    class Meta:
        node = ContactGroupNode


