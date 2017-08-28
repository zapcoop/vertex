from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_filters.backends import DjangoFilterBackend

from contacts.models import ContactGroup
from contacts.serializers import ContactGroupSerializer
from noss.api.permissions import RestrictedObjectLevelPermissions
from ..filters import ContactGroupFilterSet


class ContactGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contact groups to be viewed or edited.
    """
    queryset = ContactGroup.objects
    serializer_class = ContactGroupSerializer
    permission_classes = (RestrictedObjectLevelPermissions, )
    filter_backends = (DjangoFilterBackend,)
    filter_class = ContactGroupFilterSet

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.objects.filter(
                organization__in=self.request.user.person.organizations.all())

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset.distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Protect groups that are required to stay in the system
        if instance.pk <= 5:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
