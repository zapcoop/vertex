from django.db.models import QuerySet
from rest_framework import viewsets

from contacts.models import OrganizationDepartment
from contacts.serializers import OrganizationDepartmentSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions
from ..filters import OrganizationDepartmentFilterSet


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contact departments to be viewed or edited.
    """
    queryset = OrganizationDepartment.objects
    serializer_class = OrganizationDepartmentSerializer
    permission_classes = [RestrictedObjectLevelPermissions, ]
    filter_class = OrganizationDepartmentFilterSet

    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk')

        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = OrganizationDepartment.objects.filter(
                organization__in=self.request.user.person.organizations.all())

        if organization_pk:
            queryset = queryset.filter(organization__pk=organization_pk)

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()
