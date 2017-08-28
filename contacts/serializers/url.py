from django.db.models import Q
from rest_framework_json_api.relations import ResourceRelatedField

from contacts.models import URL, Person, Organization
from noss.api.serializermixins import FilterRelatedMixin, ValidationMixin
from rest_framework_json_api import serializers


class URLSerializer(ValidationMixin, FilterRelatedMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = URL

    person = ResourceRelatedField(
        queryset=Person.objects,
        self_link_view_name='url-relationships',
        required=False
    )

    organization = ResourceRelatedField(
        queryset=Organization.objects,
        self_link_view_name='url-relationships',
        required=False
    )

    def filter_organization(self, qs):
        request = self.context['request']
        if request.user.is_staff:
            return qs
        else:
            return qs.filter(organization__in=request.user.person.managed_organizations)

    def filter_person(self, qs):
        request = self.context['request']
        if request.user.is_staff:
            return qs
        else:
            return qs.filter(
                Q(
                    Q(
                        organizations__in=request.user.person.managed_organizations.all()
                    ) | Q(
                        departments__in=request.user.person.managed_departments.all()
                    ) | Q(
                        user=request.user.pk
                    )
                )
            ).distinct()