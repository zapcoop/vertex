from django.db import models
from django.utils.translation import ugettext_lazy as _

from vertex.models import AbstractDatedModel


def attachment_path(instance, filename):
    """
    Provide a file path that will help prevent files being overwritten, by
    putting attachments in a folder off attachments for ticket/followup_id/.
    """
    import os
    from django.conf import settings

    os.umask(0)
    path = 'service/attachments/%s/%s' % (instance.note.ticket.ticket_for_url, instance.note.id)
    att_path = os.path.join(settings.MEDIA_ROOT, path)
    if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
        if not os.path.exists(att_path):
            os.makedirs(att_path, 0o777)
    return os.path.join(path, filename)


class Attachment(AbstractDatedModel, models.Model):
    """
    Represents a file attached to a follow-up. This could come from an e-mail
    attachment, or it could be uploaded via the web interface.
    """

    note = models.ForeignKey(
        'service.Update',
        verbose_name=_('Update'),
    )

    file = models.FileField(
        _('File'),
        upload_to=attachment_path,
        max_length=1000,
    )

    filename = models.CharField(
        _('Filename'),
        max_length=1000,
    )

    mime_type = models.CharField(
        _('MIME Type'),
        max_length=255,
    )

    size = models.IntegerField(
        _('Size'),
        help_text=_('Size of this file in bytes'),
    )

    def get_upload_to(self, field_attname):
        """ Get upload_to path specific to this item """
        if not self.id:
            return u''
        return u'service/attachments/%s/%s' % (
            self.followup.ticket.ticket_for_url,
            self.followup.id
        )

    def __str__(self):
        return u'%s' % self.filename

    class Meta:
        ordering = ['upload_to', ]
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
