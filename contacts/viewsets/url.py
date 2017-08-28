from django.db.models import QuerySet, Q
from rest_framework import viewsets
from contacts.models import URL
from contacts.serializers.url import URLSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions
from ..filters import URLFilterSet


class URLViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows URLs to be viewed or edited.
    """
    serializer_class = URLSerializer
    permission_classes = (RestrictedObjectLevelPermissions, )
    filter_class = URLFilterSet
    queryset = URL.objects

    def get_queryset(self):
        organization_pk = self.kwargs.get('organization_pk')
        person_pk = self.kwargs.get('person_pk')

        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(
                Q(
                    Q(
                        organization__in=self.request.user.person.organizations.all()
                    ) | Q(
                        Q(
                            organization=None
                        ) & Q(
                            person__organization__in=self.request.user.person.organizations.all()
                        )
                    )
                )
            ).distinct()

        if organization_pk:
            queryset = queryset.filter(organization__pk=organization_pk)

        if person_pk:
            queryset = queryset.filter(person__pk=person_pk)

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()