from contacts.models import EmailDomain

__author__ = 'jsenecal'

from rest_framework_json_api import serializers


class EmailDomainSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmailDomain