from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework_filters.backends import DjangoFilterBackend

from contacts.models import Person
from contacts.serializers import PersonSerializer
from contacts.serializers.person import SetPrimaryEmailSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions
from ..filters import PersonFilterSet

User = get_user_model()


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows people to be viewed or edited.
    """
    queryset = Person.objects
    serializer_class = PersonSerializer
    permission_classes = [RestrictedObjectLevelPermissions, ]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = PersonFilterSet
    search_fields = ('last_name', 'first_name', 'nickname', 'user__username',
                     'organizations__name', 'email_addresses__email_address')

    def get_queryset(self):
        queryset = super(PersonViewSet, self).get_queryset()

        organization_pk = self.kwargs.get('organization_pk')
        managed_organization_pk = self.kwargs.get('managed_organization_pk')

        department_pk = self.kwargs.get('department_pk')
        managed_department_pk = self.kwargs.get('managed_department_pk')

        group_pk = self.kwargs.get('group_pk')

        if not self.request.user.is_staff:
            queryset = queryset.filter(organizations__in=self.request.user.person.organizations.all())

        if organization_pk:
            queryset = queryset.filter(organizations__pk=organization_pk)
        if managed_organization_pk:
            queryset = queryset.filter(managed_organizations__pk=managed_organization_pk)

        if department_pk:
            queryset = queryset.filter(departments__pk=department_pk)
        if managed_department_pk:
            queryset = queryset.filter(managed_departments__pk=managed_department_pk)

        if group_pk:
            queryset = queryset.filter(groups__pk=group_pk)

        return queryset.distinct()

    @detail_route(methods=['post'], serializer_class=SetPrimaryEmailSerializer)
    def set_primary_email(self, request, *args, **kwargs):
        person = self.get_object()
        serializer = self.get_serializer(data=request.data, person=person)
        serializer.is_valid(raise_exception=True)
        person.set_primary_email(serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)
