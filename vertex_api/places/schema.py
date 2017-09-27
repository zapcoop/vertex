import graphene
from graphene_django.filter import DjangoFilterConnectionField

from graphene_django.types import DjangoObjectType

from places.models import (
    Place,
    AddressComponent
)


class PlaceNode(DjangoObjectType):
    address_components = graphene.relay.ConnectionField("places.schema.AddressComponentNode")

    def resolve_address_components(self, args, context, info):
        return self.address_components.all()

    class Meta:
        model = Place
        filter_fields = {
            'raw_address': ['exact', 'icontains', 'istartswith'],
            'formatted_address': ['exact', 'icontains', 'istartswith'],
            'place_type': ['exact'],
            'google_place_id': ['exact'],
            'notes': ['icontains'],
            'address_components': ['exact'],
            'address_components__long_name': ['exact', 'icontains', 'istartswith'],
            'address_components__short_name': ['exact', 'icontains', 'istartswith'],
            'address_components__component_type': ['exact'],
        }
        interfaces = (graphene.relay.Node,)


class AddressComponentNode(DjangoObjectType):
    class Meta:
        model = AddressComponent
        filter_fields = {
            'long_name': ['exact', 'icontains', 'istartswith'],
            'short_name': ['exact', 'icontains', 'istartswith'],
            'component_type': ['exact'],
        }
        interfaces = (graphene.relay.Node,)


class Query(graphene.AbstractType):
    place = graphene.relay.Node.Field(PlaceNode)
    all_places = DjangoFilterConnectionField(PlaceNode)

    address_component = graphene.relay.Node.Field(AddressComponentNode)
    all_address_components = DjangoFilterConnectionField(AddressComponentNode)
