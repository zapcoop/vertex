from rest_framework import viewsets

from ..models import Note
from ..serializers import NoteSerializer
from ..filters import NoteFilterSet


class NoteViewSet(viewsets.ModelViewSet):

    serializer_class = NoteSerializer
    queryset = Note.objects.all()
    filter_class = NoteFilterSet

    def perform_create(self, serializer):
        serializer.save(person=self.request.user.person)
