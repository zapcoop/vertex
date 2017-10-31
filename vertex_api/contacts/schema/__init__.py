import graphene
from graphene_django.filter import DjangoFilterConnectionField

from contacts.schema.nodes import (ContactGroupNode,
                                   OrganizationNode,
                                   PersonNode)

class Query(graphene.ObjectType):
    contact_group = graphene.relay.Node.Field(ContactGroupNode)
    all_contact_groups = DjangoFilterConnectionField(ContactGroupNode)

    organization = graphene.relay.Node.Field(OrganizationNode)
    all_organizations = DjangoFilterConnectionField(OrganizationNode)

    person = graphene.relay.Node.Field(PersonNode)
    all_people = DjangoFilterConnectionField(PersonNode)

class Mutation(graphene.ObjectType):
     pass