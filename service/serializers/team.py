from rest_framework_json_api.serializers import HyperlinkedModelSerializer
from rest_framework_json_api.relations import ResourceRelatedField
from django_mailbox.models import Mailbox

from ..models import Team
from contacts.models import OrganizationDepartment


class TeamSerializer(HyperlinkedModelSerializer):

    mailbox = ResourceRelatedField(
        queryset=Mailbox.objects,
        self_link_view_name='team-relationships'
    )

    allowed_organization_departments = ResourceRelatedField(
        many=True,
        queryset=OrganizationDepartment.objects,
        related_link_view_name='team-departments-list',
        related_link_url_kwarg='team_pk',
        self_link_view_name='team-relationships'
    )

    class Meta:
        model = Team
