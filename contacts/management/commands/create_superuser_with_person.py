"""Customized version of django's createsuperuser command, to create a person object at the same time."""
from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth import get_user_model

from contacts.models import Person, EmailAddress


def create_superuser_decorator(func):
    def inner_function(*args, **kwargs):
        superuser = func(*args, **kwargs)
        person = Person.objects.create(user=superuser)
        EmailAddress.objects.create(email_address=superuser.email, person=person, primary=True)
    return inner_function


class Command(createsuperuser.Command):
    help = 'Create a superuser and associated Person object'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.UserModel.objects.create_superuser = create_superuser_decorator(self.UserModel.objects.create_superuser)
