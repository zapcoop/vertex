from rest_framework import viewsets

from vertex.api.permissions import RestrictedObjectLevelPermissions
from service.models import Team
from service.serializers import TeamSerializer
from ..filters import TeamFilterSet


class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows service departments to be viewed or edited.
    """
    serializer_class = TeamSerializer
    permission_classes = (RestrictedObjectLevelPermissions, )
    queryset = Team.objects.all()
    filter_class = TeamFilterSet
    # def get_queryset(self):
    #     if self.request.user.is_superuser:
    #         queryset = Department.objects
    #     elif self.request.user.is_staff:
    #         queryset = Department.objects.filter(
    #             allowed_organization_departments__in=self.request.user.person.departments.all()
    #         )
    #     else:
    #         queryset = Department.objects.none()
    #     queryset = self.filter_queryset_by_parents_lookups(queryset)
    #     if isinstance(queryset, QuerySet):
    #         # Ensure queryset is re-evaluated on each request.
    #         queryset = queryset.all()
    #     return queryset.distinct()
