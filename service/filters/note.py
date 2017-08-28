from noss.filters import IdListFilterSet
from ..models import Note


class NoteFilterSet(IdListFilterSet):

    class Meta:
        model = Note
