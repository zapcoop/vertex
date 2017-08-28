from django.db.models import Q
from rest_framework_json_api.relations import ResourceRelatedField

from contacts.models import PhoneNumber, Person, Organization
from noss.api.serializermixins import FilterRelatedMixin, ValidationMixin

__author__ = 'jsenecal'

from rest_framework_json_api import serializers


class PhoneNumberSerializer(ValidationMixin, FilterRelatedMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PhoneNumber

    person = ResourceRelatedField(
        queryset=Person.objects,
        self_link_view_name='phonenumber-relationships',
        required=False,
        default=None
    )

    organization = ResourceRelatedField(
        queryset=Organization.objects,
        self_link_view_name='phonenumber-relationships',
        required=False,
        default=None
    )

    extension = serializers.CharField(
        max_length=10,
        allow_blank=True,
        required=False,
        default=None
    )

    def filter_organization(self, qs):
        request = self.context['request']
        if request.user.is_staff:
            return qs
        else:
            return request.user.person.managed_organizations

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