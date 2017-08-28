from django.db.models import Q, QuerySet
from rest_framework import viewsets
from contacts.models import PhoneNumber
from contacts.serializers import PhoneNumberSerializer
from ..filters import PhoneNumberFilterSet

from noss.api.permissions import RestrictedObjectLevelPermissions


class PhoneNumberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows phone numbers to be viewed or edited.
    """
    serializer_class = PhoneNumberSerializer
    permission_classes = (RestrictedObjectLevelPermissions, )
    filter_class = PhoneNumberFilterSet
    queryset = PhoneNumber.objects

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