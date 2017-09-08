from django.db.models import QuerySet

from contacts.models import Organization, Person
from contacts.serializers import OrganizationSerializer, PersonSerializer
from vertex.api.serializermixins import FilterRelatedMixin
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.utils import format_relation_name
from tags.models import Tag
from tags.serializers import TagSerializer
from .team import TeamSerializer
from .update import UpdateSerializer
from ..models import Ticket, Team


class TicketSerializer(FilterRelatedMixin, serializers.ModelSerializer):
    included_serializers = {
        'updates': UpdateSerializer,
        'teams': TeamSerializer,
        'organization': OrganizationSerializer,
        'assigned_to': PersonSerializer,
        'signaled_by': PersonSerializer,
        'created_by': PersonSerializer,
        'parent': 'self',
        'duplicate_of': 'self',
        'tags': TagSerializer,
    }

    updates = ResourceRelatedField(
        required=False,
        many=True,
        read_only=True,
        self_link_view_name='ticket-relationships',
        related_link_view_name='ticket-updates-list',
        related_link_url_kwarg='ticket_pk'
    )
    teams = ResourceRelatedField(queryset=Team.objects, required=False, many=True)
    organization = ResourceRelatedField(queryset=Organization.objects)
    assigned_to = ResourceRelatedField(queryset=Person.objects, required=False)
    signaled_by = ResourceRelatedField(queryset=Person.objects, required=False)
    created_by = ResourceRelatedField(queryset=Person.objects, required=False)
    parent = ResourceRelatedField(queryset=Ticket.objects, required=False)
    duplicate_of = ResourceRelatedField(queryset=Ticket.objects, required=False)
    tags = ResourceRelatedField(queryset=Tag.objects, required=False, many=True)

    def update(self, instance, validated_data):
        changed_fields = dict()

        for field, value in validated_data.items():
            if value != getattr(instance, field):
                if isinstance(self.fields.get(field), serializers.PrimaryKeyRelatedField):
                    changed_fields[field] = value.id
                else:
                    changed_fields[field] = value

        if len(changed_fields) > 0:
            update_serializer = UpdateSerializer(
                from_ticket=True,
                data={
                    'ticket': {'type': format_relation_name('Ticket'), 'id': instance.id},
                    'changed_fields': changed_fields
                },
                context=self.context
            )
            update_serializer.is_valid(raise_exception=True)
            update_serializer.save()

        instance = Ticket.objects.get(pk=instance.pk)
        return instance

    def filter_tags(self, queryset):
        request = self.context.get('request')
        if request is not None:
            user = request.user

            if hasattr(user, 'person'):
                queryset = queryset.filter(person=user.person) | queryset.filter(personal=False)
            else:
                queryset = queryset.filter(personal=False)

            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()

        return queryset.distinct()

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'teams', 'signaled_by', 'organization', 'created_by',
                  'assigned_to', 'signaled_by', 'status', 'description', 'resolution', 'priority',
                  'signaled_date', 'due_date', 'last_escalation', 'updates', 'parent',
                  'duplicate_of', 'tags')
