import json

import graphene
from django.contrib.gis.db.models import PointField

from graphene_django.converter import convert_django_field, convert_field_to_string

@convert_django_field.register(PointField)
def convert_point_field(field, registry=None):
    return graphene.String(description=field.help_text, required=not field.null)


import contacts.schema
import sites.schema


class Query(sites.schema.Query, contacts.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(query=Query)