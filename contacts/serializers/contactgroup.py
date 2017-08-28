from rest_framework_json_api.serializers import HyperlinkedModelSerializer
from rest_framework_json_api.relations import ResourceRelatedField

from contacts.models import ContactGroup, Organization, Person


class ContactGroupSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ContactGroup

    organizations = ResourceRelatedField(
        many=True,
        queryset=Organization.objects,
        related_link_view_name='group-organizations-list',
        related_link_url_kwarg='group_pk',
        self_link_view_name='group-relationships'
    )

    people = ResourceRelatedField(
        many=True,
        queryset=Person.objects,
        related_link_view_name='group-people-list',
        related_link_url_kwarg='group_pk',
        self_link_view_name='group-relationships',
    )
