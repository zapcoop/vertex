__author__ = 'Jonathan Senecal <jonathan@zap.coop>'
import rules


@rules.predicate
def is_department_manager(person, department):
    if department:
        return department.managers.filter(pk=person.pk).exists()
    else:
        return False


@rules.predicate
def is_department_member(person, department):
    if department:
        return department.people.filter(pk=person.pk).exists()
    else:
        return person.departments.exists()
