from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

from noss import rules
from noss.rules.predicates import has_django_permission, is_staff, is_superuser
from ..rules.note import is_note_creator

from noss.models import AbstractDatedModel


class Note(AbstractDatedModel, models.Model):
    """
    A note is an internal communication between staff members, associated with
    an update to the ticket. Notes should only visible to staff users.
    """
    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
        ordering = ('created_at', )

    body = models.TextField(
        _('Body')
    )

    person = models.ForeignKey('contacts.Person', editable=False)

    update = models.ForeignKey('service.Update', related_name='notes')

    @property
    def editable(self):
        age = timezone.now() - self.created_at
        return age < timedelta(seconds=settings.TICKET_NOTE_ALLOW_EDIT_DURATION)

rules.add_perm('service.view_note', is_superuser | is_staff)
rules.add_perm('service.add_note', is_superuser | is_staff & has_django_permission('service.add_note'))
rules.add_perm('service.change_note', is_superuser | is_staff & has_django_permission('service.change_note') | is_note_creator)
rules.add_perm('service.delete_note', is_superuser | is_staff & has_django_permission('service.delete_note') | is_note_creator)
