from django.db.models import QuerySet
from rest_framework import viewsets

from contacts.models import EmailDomain
from contacts.serializers import EmailDomainSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions
from ..filters import EmailDomainFilterSet


class EmailDomainViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows domain names to be viewed or edited.
    """
    queryset = EmailDomain.objects
    serializer_class = EmailDomainSerializer

    permission_classes = (RestrictedObjectLevelPermissions, )
    filter_class = EmailDomainFilterSet

    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk')

        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(
                organization__in=self.request.user.person.managed_organizations.all())

        if organization_pk:
            queryset = queryset.filter(organization__pk=organization_pk)

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()
