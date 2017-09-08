from django.db import models
from django.db.models.query import QuerySet
from django.db.models.deletion import Collector
from django.db import router, transaction
from django.utils import timezone


def collect_and_remove(objs, using):
        collector = Collector(using=using)
        with transaction.atomic():
            now = timezone.now()
            collector.collect(objs)
            for qs in collector.fast_deletes:
                if issubclass(qs.model, SoftDeletableModel):
                    # only touch related objects which aren't already softdeleted
                    # to prevent clobbering the removed date on already removed objects
                    qs.filter(removed__isnull=True).update(removed=now)
            for model, instances in collector.data.items():
                if issubclass(model, SoftDeletableModel):
                    pks = [obj.pk for obj in instances]
                    qs = QuerySet(model=model, using=collector.using)
                    qs.filter(pk__in=pks).filter(removed__isnull=True).update(removed=now)


class SoftDeletableQuerySet(QuerySet):
    def delete(self, force=True):
        if not force:
            assert self.query.can_filter(), \
                "Cannot use 'limit' or 'offset' with delete."

            queryset = self._clone()

            # The delete is actually 2 queries - one to find related objects,
            # and one to delete. Make sure that the discovery of related
            # objects is performed on the same database as the deletion.
            queryset._for_write = True

            # Disable non-supported fields.
            queryset.query.select_for_update = False
            queryset.query.select_related = False
            queryset.query.clear_ordering(force_empty=True)

            collect_and_remove(queryset, queryset.db)

        else:
            super(SoftDeletableQuerySet, self).delete()

    @transaction.atomic
    def restore(self):
        for obj in self.all():  # TODO: figure out whether it's possible to avoid this
            obj.restore()
    restore.queryset_only = False

    def deleted(self):
        return self.filter(removed__isnull=False)

    def non_deleted(self):
        return self.filter(removed__isnull=True)


SoftDeletableManager = models.Manager.from_queryset(SoftDeletableQuerySet)
SoftDeletableManager.use_for_related_fields = True


class NonDeletedManager(SoftDeletableManager):
    def get_queryset(self):
        return super(NonDeletedManager, self).get_queryset().non_deleted()


class DeletedManager(SoftDeletableManager):
    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().deleted()


class SoftDeletableModel(models.Model):
    """Never edit the `removed` field directly on the instance. Bad things will happen. Kittens will be sad."""
    class Meta:
        abstract = True

    removed = models.DateTimeField(default=None, null=True, blank=True, editable=False)

    objects = SoftDeletableManager()
    non_deleted_objects = NonDeletedManager()
    deleted_objects = DeletedManager()
    _base_manager = SoftDeletableManager()

    def delete(self, *args, **kwargs):
        force = kwargs.pop('force', False)
        using = kwargs.get('using')
        if not force:
            using = using or router.db_for_write(self.__class__, instance=self)
            assert self._get_pk_val() is not None, (
                "%s object can't be deleted because its %s attribute is set to None." %
                (self._meta.object_name, self._meta.pk.attname)
            )
            collect_and_remove([self], using)
            self.refresh_from_db(fields=['removed'])
        else:
            super(SoftDeletableModel, self).delete(*args, **kwargs)

    def restore(self):
        if self.removed:
            with transaction.atomic():
                collector = Collector(using=router.db_for_write(self.__class__, instance=self))
                collector.collect([self])
                for qs in collector.fast_deletes:
                    if issubclass(qs.model, SoftDeletableModel):
                        # don't restore related objects that were deleted before this object
                        qs = qs.filter(removed__gte=self.removed)
                        qs.update(removed=None)
                for model, instances in collector.data.items():
                    if issubclass(model, SoftDeletableModel):
                        pks = [obj.pk for obj in instances]
                        qs = QuerySet(model=model, using=collector.using).filter(pk__in=pks)
                        qs = qs.filter(removed__gte=self.removed)
                        qs.update(removed=None)
            self.refresh_from_db(fields=['removed'])
