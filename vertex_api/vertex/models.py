import datetime
import json
from time import timezone

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class AbstractDatedModel(models.Model):
    """A mixin for adding created and modified timestamps to a model."""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at")
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name=_("modified at")
    )

    def modified_recently(self):
        return self.modified_at >= timezone.now() - datetime.timedelta(days=1)


class AbstractNullUniqueModel(models.Model):
    class Meta:
        abstract = True

    def clean(self):
        """
        Check for instances with null values in unique_together fields.
        """
        super(AbstractNullUniqueModel, self).clean()

        for field_tuple in self._meta.unique_together[:]:
            unique_filter = {}
            unique_fields = []
            null_found = False
            for field_name in field_tuple:
                field_value = getattr(self, field_name)
                if getattr(self, field_name) is None:
                    unique_filter['%s__isnull' % field_name] = True
                    null_found = True
                else:
                    unique_filter['%s' % field_name] = field_value
                    unique_fields.append(field_name)
            if null_found:
                unique_queryset = self.__class__.objects.filter(**unique_filter)
                if self.pk:
                    unique_queryset = unique_queryset.exclude(pk=self.pk)
                if unique_queryset.exists():
                    msg = self.unique_error_message(self.__class__, tuple(unique_fields))
                    raise ValidationError(msg)