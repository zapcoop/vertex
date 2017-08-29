from django.db.models import QuerySet
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed

from service.models import Update
from service.serializers import UpdateSerializer
from ..filters import UpdateFilterSet

from vertex.api.permissions import RestrictedObjectLevelPermissions


class UpdateViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Update.objects
    serializer_class = UpdateSerializer
    permission_classes = (RestrictedObjectLevelPermissions,)
    filter_class = UpdateFilterSet

    def get_queryset(self):
        queryset = self.queryset
        if 'ticket_pk' in self.kwargs:
            queryset = queryset.filter(ticket__pk=self.kwargs['ticket_pk'])

        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(ticket__organizations__in=self.request.user.person.organizations.all())
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()

    def partial_update(self, request, *args, **kwargs):
        if self.get_object().editable:
            kwargs['partial'] = True
            return super(UpdateViewSet, self).update(request, *args, **kwargs)
        else:
            raise PermissionDenied("This update object cannot be edited.")

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)
