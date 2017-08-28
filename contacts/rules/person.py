import rules


@rules.predicate
def is_same_organization(person, other_person):
    if other_person:
        return len(set(person.organizations.all()).intersection(set(other_person.organizations.all()))) > 0
    else:
        return person is not None


@rules.predicate
def is_object_person_manager(person, obj):
    if obj:
        if obj.person:
            return obj.person.departments.filter(managers__pk=person.pk).exists()
        else:
            return False
    else:
        return person.managed_departments.exists()
