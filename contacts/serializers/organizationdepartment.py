from contacts.models import OrganizationDepartment, Person
from noss.api.serializermixins import FilterRelatedMixin
from rest_framework_json_api.serializers import HyperlinkedModelSerializer
from rest_framework_json_api.relations import ResourceRelatedField


class OrganizationDepartmentSerializer(FilterRelatedMixin, HyperlinkedModelSerializer):
    class Meta:
        model = OrganizationDepartment

    people = ResourceRelatedField(
        related_link_view_name='department-people-list',
        related_link_url_kwarg='department_pk',
        self_link_view_name='organizationdepartment-relationships',
        queryset=Person.objects,
        many=True
    )
    managers = ResourceRelatedField(
        related_link_view_name='department-managers-list',
        related_link_url_kwarg='managed_department_pk',
        self_link_view_name='organizationdepartment-relationships',
        queryset=Person.objects,
        many=True
    )

    def filter_organization(self, qs):
        try:
            request = self.context['request']
        except KeyError:
            return qs
        else:
            if request.user.is_staff:
                return qs
            else:
                return request.user.person.managed_organizations

    def filter_people(self, qs):
        try:
            request = self.context['request']
        except KeyError:
            return qs
        else:
            if request.user.is_staff:
                return qs
            else:
                user_organizations = request.user.person.managed_organizations.all()
                return Person.objects.filter(organizations__in=user_organizations).order_by('pk')

    def filter_managers(self, qs):
        return self.filter_people(qs)
