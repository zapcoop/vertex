from django.db.models import Q

from contacts.models import EmailAddress
from noss.api.serializermixins import FilterRelatedMixin, ValidationMixin
from rest_framework_json_api.relations import ResourceRelatedField

__author__ = 'jsenecal'

from rest_framework_json_api import serializers


class EmailAddressSerializer(ValidationMixin, FilterRelatedMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmailAddress

    serializer_related_field = ResourceRelatedField

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

    def filter_person(self, qs):
        try:
            request = self.context['request']
        except KeyError:
            return qs
        else:
            if request.user.is_staff:
                return qs
            else:
                return qs.filter(
                    Q(
                        Q(
                            organizations__in=request.user.person.managed_organizations.all()
                        ) | Q(
                            departments__in=request.user.person.managed_departments.all())
                    )
                )