"""noss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter

from contacts.views import OrganizationRelationshipsView, PeopleRelationshipsView, \
    OrganizationDepartmentRelationshipsView, CreateLoginView, URLRelationshipView, PhoneNumberRelationshipView, \
    ContactGroupRelationshipView
from rest_framework_nested import routers
from contacts.viewsets import (OrganizationViewSet, DepartmentViewSet, PersonViewSet, ContactGroupViewSet,
                               EmailAddressViewSet, PhoneNumberViewSet, URLViewSet, EmailDomainViewSet)


router = DefaultRouter(trailing_slash=False)

router.register(r'organizations', OrganizationViewSet)
router.register(r'departments', DepartmentViewSet, base_name='organizationdepartment')
router.register(r'people', PersonViewSet)
router.register(r'groups', ContactGroupViewSet)
router.register(r'emailaddresses', EmailAddressViewSet)
router.register(r'phonenumbers', PhoneNumberViewSet)
router.register(r'urls', URLViewSet)
router.register(r'emaildomains', EmailDomainViewSet)

group_router = routers.NestedSimpleRouter(router, r'groups', lookup='group', trailing_slash=False)
group_router.register(r'organizations', OrganizationViewSet, base_name='group-organizations')
group_router.register(r'people', PersonViewSet, base_name='group-people')

organizations_parent_router = routers.NestedSimpleRouter(
    router, r'organizations', lookup='parent', trailing_slash=False
)
organizations_parent_router.register(r'children', OrganizationViewSet, base_name='organization-children')

organizations_reseller_router = routers.NestedSimpleRouter(
    router, r'organizations', lookup='reseller', trailing_slash=False
)
organizations_reseller_router.register(r'customers', OrganizationViewSet, base_name='organization-customers')

organizations_customer_router = routers.NestedSimpleRouter(
    router, r'organizations', lookup='customer', trailing_slash=False
)
organizations_customer_router.register(r'resellers', OrganizationViewSet, base_name='organization-resellers')

organizations_organization_router = routers.NestedSimpleRouter(
    router, r'organizations', lookup='organization', trailing_slash=False
)
organizations_organization_router.register(r'departments', DepartmentViewSet, base_name='organization-departments')
organizations_organization_router.register(r'emaildomains', EmailDomainViewSet, base_name='organization-emaildomains')
organizations_organization_router.register(
    r'emailaddresses', EmailAddressViewSet, base_name='organization-emailaddresses'
)
organizations_organization_router.register(r'phonenumbers', PhoneNumberViewSet, base_name='organization-phonenumbers')
organizations_organization_router.register(r'urls', URLViewSet, base_name='organization-urls')
organizations_organization_router.register(r'people', PersonViewSet, base_name='organization-people')

organizations_managed_organization_router = routers.NestedSimpleRouter(
    router, r'organizations', lookup='managed_organization', trailing_slash=False
)
organizations_managed_organization_router.register(
    r'administrators', PersonViewSet, base_name='organization-administrators'
)

people_person_router = routers.NestedSimpleRouter(router, r'people', lookup='person', trailing_slash=False)
people_person_router.register(r'departments', DepartmentViewSet, base_name='person-departments')
people_person_router.register(r'emailaddresses', EmailAddressViewSet, base_name='person-emailaddresses')
people_person_router.register(r'phonenumbers', PhoneNumberViewSet, base_name='person-phonenumbers')
people_person_router.register(r'urls', URLViewSet, base_name='person-urls')
people_person_router.register(r'organizations', OrganizationViewSet, base_name='person-organizations')

people_manager_router = routers.NestedSimpleRouter(router, r'people', lookup='manager', trailing_slash=False)
people_manager_router.register(r'organizations', OrganizationViewSet, base_name='person-managedorganizations')
people_manager_router.register(r'departments', DepartmentViewSet, base_name='person-manageddepartments')

departments_department_router = routers.NestedSimpleRouter(
    router, r'departments', lookup='department', trailing_slash=False
)
departments_department_router.register(r'people', PersonViewSet, base_name='department-people')

departments_managed_department_router = routers.NestedSimpleRouter(
    router, r'departments', lookup='managed_department', trailing_slash=False
)
departments_managed_department_router.register(r'managers', PersonViewSet, base_name='department-managers')

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
    url(r'^', include(group_router.urls)),
    url(r'^', include(organizations_parent_router.urls)),
    url(r'^', include(organizations_reseller_router.urls)),
    url(r'^', include(organizations_customer_router.urls)),
    url(r'^', include(organizations_organization_router.urls)),
    url(r'^', include(organizations_managed_organization_router.urls)),
    url(r'^', include(people_person_router.urls)),
    url(r'^', include(people_manager_router.urls)),
    url(r'^', include(departments_department_router.urls)),
    url(r'^', include(departments_managed_department_router.urls)),
    url(r'^organizations/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        OrganizationRelationshipsView.as_view(),
        name='organization-relationships'),
    url(r'^people/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        PeopleRelationshipsView.as_view(),
        name='person-relationships'),
    url(r'^department/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        OrganizationDepartmentRelationshipsView.as_view(),
        name='organizationdepartment-relationships'),
    url(r'^urls/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        URLRelationshipView.as_view(), name='url-relationships'),
    url(r'^phonenumbers/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        PhoneNumberRelationshipView.as_view(), name='phonenumber-relationships'),
    url(r'^groups/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
        ContactGroupRelationshipView.as_view(), name='group-relationships'),
    url(r'^people/(?P<pk>[^/.]+)/create_login', CreateLoginView.as_view(), name='person-createlogin')
)
