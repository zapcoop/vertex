from django.db import transaction

from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from ..models import Update, Team, Ticket, TicketChange, Note
from contacts.models import Person, Organization


class ChangedFieldSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    priority = serializers.IntegerField(min_value=1, max_value=5, required=False)
    resolution = serializers.CharField(required=False)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        queryset=Person.objects.all()  # TODO restrict this queryset to something more sensible
    )

    signaled_by = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        queryset=Person.objects.all()
    )

    organization = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        queryset=Organization.objects.all()
    )

    department = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        queryset=Team.objects.all()
    )


class UpdateSerializer(serializers.ModelSerializer):

    included_serializers = {
        'person': 'contacts.serializers.PersonSerializer',
        'notes': 'service.serializers.NoteSerializer'
    }

    ticket = ResourceRelatedField(
        queryset=Ticket.objects.all(),
        self_link_view_name='update-relationships'
    )
    notes = ResourceRelatedField(
        many=True,
        read_only=True,
        self_link_view_name='update-relationships',
        related_link_view_name='update-notes-list',
        related_link_url_kwarg='update_pk'
    )
    ticket_changes = serializers.ListField(child=serializers.DictField(), required=False, read_only=True)
    changed_fields = ChangedFieldSerializer(required=False, write_only=True)

    def __init__(self, *args, from_ticket=False, **kwargs):
        super(UpdateSerializer, self).__init__(*args, **kwargs)
        if not from_ticket:
            # when instantiated by TicketSerializer, keep changed_fields field
            # otherwise, from_ticket is false and we remove the changed_fields field
            # because it shouldn't be externally available
            self.fields.pop('changed_fields', None)

    def validate(self, data):
        if 'changed_fields' in data:
            self._remove_dummy_changed_fields(data)
            if len(data['changed_fields']) == 0:
                del data['changed_fields']

        return data

    def _remove_dummy_changed_fields(self, data):
        ticket = data['ticket']
        for field, new_value in data['changed_fields'].items():
            old_value = getattr(ticket, field)
            if old_value == new_value:
                del data['changed_fields'][field]

    def create(self, validated_data):
        with transaction.atomic():
            changed_fields = validated_data.pop('changed_fields', {})
            person = self.context['request'].user.person
            update = Update.objects.create(person=person, **validated_data)
            self._apply_ticket_changes(validated_data['ticket'], changed_fields, update)
            return update

    def _apply_ticket_changes(self, ticket, changed_fields, update):
        for field, new_value in changed_fields.items():
            TicketChange.objects.create(
                field=field,
                update=update,
                old_value=getattr(ticket, field),
                new_value=new_value
            )
            setattr(ticket, field, new_value)
        ticket.save()

    # def update(self, instance, validated_data):
    #     editable_fields_on_update = ('display_time', 'body', 'duration', 'billable_hours')
    #

    class Meta:
        model = Update
        fields = ('ticket', 'display_time', 'body', 'person', 'duration', 'billable_hours', 'ticket_changes',
                  'changed_fields', 'notes')
