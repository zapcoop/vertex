from rest_framework_json_api import serializers, relations

from ..models import Note, Update


class NoteSerializer(serializers.ModelSerializer):
    # add update field in __init__ to avoid clobbering the serializer's update method
    def __init__(self, *args, **kwargs):
        super(NoteSerializer, self).__init__(*args, **kwargs)
        self.fields['update'] = relations.ResourceRelatedField(queryset=Update.objects)

    included_serializers = {
        'person': 'contacts.serializers.PersonSerializer'
    }

    person = relations.ResourceRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = '__all__'
