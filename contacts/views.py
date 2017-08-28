from django.db import transaction
from rest_framework.response import Response
from contacts.models import Organization, Person, OrganizationDepartment, URL, PhoneNumber, EmailAddress, ContactGroup
from contacts.serializers import CreateLoginSerializer
from rest_framework_json_api.views import RelationshipView
from rest_framework import generics
from noss.api.permissions import RestrictedObjectLevelPermissions

from rest_framework.reverse import reverse


class OrganizationRelationshipsView(RelationshipView):
    queryset = Organization.objects


class OrganizationDepartmentRelationshipsView(RelationshipView):
    queryset = OrganizationDepartment.objects


class PeopleRelationshipsView(RelationshipView):
    queryset = Person.objects


class URLRelationshipView(RelationshipView):
    queryset = URL.objects


class PhoneNumberRelationshipView(RelationshipView):
    queryset = PhoneNumber.objects


class ContactGroupRelationshipView(RelationshipView):
    queryset = ContactGroup.objects


class CreateLoginView(generics.GenericAPIView):
    resource_name = 'action'
    queryset = Person.objects  # for permissions
    permission_classes = [RestrictedObjectLevelPermissions]
    serializer_class = CreateLoginSerializer

    def get_serializer_context(self):
        context = super(CreateLoginView, self).get_serializer_context()
        context['person'] = self.get_object()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "login": reverse('user-detail', args=(serializer.instance.id,), request=request)
        })
