from django.db.models import QuerySet
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from contacts.models import Organization
from contacts.serializers import OrganizationSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows organizations to be viewed or edited.
    """
    queryset = Organization.non_deleted_objects
    serializer_class = OrganizationSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'reference', 'parent__name')
    permission_classes = [RestrictedObjectLevelPermissions, ]
    ordering = ('name', 'id', 'reference')

    def get_queryset(self):
        group_pk = self.kwargs.get('group_pk')
        parent_pk = self.kwargs.get('parent_pk')
        customer_pk = self.kwargs.get('customer_pk')
        reseller_pk = self.kwargs.get('reseller_pk')
        person_pk = self.kwargs.get('person_pk')

        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = (self.request.user.person.organizations
                        if hasattr(self.request.user, 'person')
                        else Organization.objects.none())

        if group_pk:
            queryset = queryset.filter(groups__pk=group_pk)
        if parent_pk:
            queryset = queryset.filter(parent__pk=parent_pk)
        if customer_pk:
            queryset = queryset.filter(customers__pk=customer_pk)
        if reseller_pk:
            queryset = queryset.filter(resellers__pk=reseller_pk)
        if person_pk:
            queryset = queryset.filter(people__pk=person_pk)

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        queryset = (queryset
                    .select_related('parent')
                    .prefetch_related('children', 'people', 'customers', 'administrators', 'departments'))
        return queryset.distinct()

    @detail_route(methods=['get'])
    def parent(self, request, pk=None):
        instance = self.get_object()
        parent = instance.parent
        if parent:
            serializer = self.get_serializer(parent)
            return Response(serializer.data)
        else:
            raise Http404


class OrganizationRelatedViewSetMixin(GenericViewSet):
    # def create(self, request, *args, **kwargs):
    # organization_pk = kwargs[compose_parent_pk_kwarg_name('organization')]
    # request.data['organization'] = organization_pk
    #     return super(OrganizationRelatedViewSetMixin, self).create(request, *args, **kwargs)
    #
    # def update(self, request, *args, **kwargs):
    #     organization_pk = kwargs[compose_parent_pk_kwarg_name('organization')]
    #     request.data['organization'] = organization_pk
    #     return super(OrganizationRelatedViewSetMixin, self).update(request, *args, **kwargs)
    pass