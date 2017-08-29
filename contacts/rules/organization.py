__author__ = 'Jonathan Senecal <jonathan@zap.coop>'
import rules


@rules.predicate
def is_organization_member(person, organization):
    if organization:
        return organization.people.filter(pk=person.pk).exists()
    else:
        return person.organizations.exists()


@rules.predicate
def is_organization_admin(person, organization):
    if organization:
        return organization.administrators.filter(pk=person.pk).exists()
    else:
        return person.managed_organizations.exists()


@rules.predicate
def is_organization_department_manager(person, organization):
    if organization:
        return person.managed_departments.filter(organization=organization).exists()
    else:
        return person.managed_departments.exists()


# Organization child objects

@rules.predicate
def is_object_organization_admin(person, obj):
    if obj:
        if hasattr(obj, 'organization') and obj.organization:
            return obj.organization.administrators.filter(pk=person.pk).exists()
        if hasattr(obj, 'organizations'):
            return obj.organizations.filter(administrators__pk=person.pk).exists()
    else:
        return person.managed_organizations.exists()


@rules.predicate
def is_object_organization_member(person, obj):
    if obj:
        if hasattr(obj, 'organization') and obj.organization:
            return obj.organization.people.filter(pk=person.pk).exists()
        if hasattr(obj, 'organizations'):
            return obj.organizations.filter(people__pk=person.pk).exists()
    else:
        return person.organizations.exists()


@rules.predicate
def is_object_organization_department_manager(person, object):
    if object:
        if object.organization:
            return person.managed_departments.filter(organization=object.organization).exists()
    else:
        return person.managed_departments.exists()
