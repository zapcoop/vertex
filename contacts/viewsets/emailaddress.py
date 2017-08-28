from django.db.models import Q, QuerySet
from rest_framework import viewsets
from contacts.filters import EmailAddressFilterSet

from contacts.models import EmailAddress
from contacts.serializers.emailaddress import EmailAddressSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions


class EmailAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows organizations email addresses to be viewed or edited.
    """
    queryset = EmailAddress.objects
    serializer_class = EmailAddressSerializer
    filter_class = EmailAddressFilterSet
    permission_classes = [RestrictedObjectLevelPermissions, ]

    def get_queryset(self):
        person_pk = self.kwargs.get('person_pk')
        if person_pk:
            return self.queryset.filter(person__pk=person_pk)
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

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()
