__author__ = 'infinity'
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from rules import predicate


def has_django_permission(permission, obj=None):
    name = 'has_django_permission:%s' % permission

    @predicate(name)
    def fn(person):
        for backend in auth.get_backends():
            if not isinstance(backend, ModelBackend):
                continue
            try:
                if backend.has_perm(person.user, permission, obj):
                    return True
            except PermissionDenied:
                return False
        return False

    return fn


@predicate
def is_verified(person):
    return person.user.is_verified


@predicate
def is_authenticated(person):
    if not hasattr(person.user, 'is_authenticated'):
        return False  # not a user model
    return person.user.is_authenticated()


@predicate
def is_superuser(person):
    if not hasattr(person.user, 'is_superuser'):
        return False  # swapped user model, doesn't support is_superuser
    return person.user.is_superuser


@predicate
def is_staff(person):
    if not hasattr(person.user, 'is_staff'):
        return False  # swapped user model, doesn't support is_staff
    return person.user.is_staff


@predicate
def is_active(person):
    if not hasattr(person.user, 'is_active'):
        return False  # swapped user model, doesn't support is_active
    return person.user.is_active