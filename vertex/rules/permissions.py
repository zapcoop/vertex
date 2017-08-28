from django.core.exceptions import PermissionDenied
from rules.rulesets import RuleSet
from django.contrib.auth.models import User
from django.apps import apps


permissions = RuleSet()


def add_perm(name, pred):
    permissions.add_rule(name, pred)


def remove_perm(name):
    permissions.remove_rule(name)


def perm_exists(name):
    return permissions.rule_exists(name)


def has_perm(name, *args, **kwargs):
    if permissions.test_rule(name, *args, **kwargs):
        return True
    else:
        raise PermissionDenied


class ObjectPermissionBackend(object):
    def authenticate(self, username, password):
        return None

    def has_perm(self, user_or_person, perm, *args, **kwargs):
        # can't import contacts.Person directly because this would create a circular import dependency
        Person = apps.get_model('contacts', 'Person')

        if isinstance(user_or_person, Person):
            return has_perm(perm, user_or_person, *args, **kwargs)
        elif isinstance(user_or_person, User):
            if user_or_person.person:
                return has_perm(perm, user_or_person.person, *args, **kwargs)

        raise PermissionDenied

    def has_module_perms(self, user, app_label):
        return has_perm(app_label, user)
