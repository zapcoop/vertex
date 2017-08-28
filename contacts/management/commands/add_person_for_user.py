from django.core.management.base import BaseCommand
from django.core import exceptions
from django.contrib.auth import get_user_model
from contacts.models import Person, EmailAddress


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def add_arguments(self, parser):
        parser.add_argument(
            '--all_superusers',
            '-a',
            action='store_true',
            dest='all',
            default=False,
            help='Create a Person object for all superusers that are missing one.'
        )

    def handle(self, *args, **options):
        if options['all']:
            for user in self.UserModel.objects.filter(is_superuser=True):
                self._create_person_for_user(user)

        else:
            try:
                while True:
                    username = input("Create a person for user. Enter username: ")
                    try:
                        user = self.UserModel.objects.get(username=username)
                        self._create_person_for_user(user)
                    except self.UserModel.DoesNotExist:
                        self.stdout.write("No user with username {} could be found.".format(username))
                    again = input("Create a Person object for another user? (y/N) ")
                    if not again.strip().lower() in ('y', 'yes'):
                        break

            except KeyboardInterrupt:
                self.stdout.write("Exiting...")
                return

    def _create_person_for_user(self, user):
        if Person.objects.filter(user=user).exists():
            self.stdout.write("A Person object already exists for user {}".format(user.username))
        else:
            self.stdout.write("Creating a Person object for user {}".format(user.username))
            first_name, last_name = user.first_name, user.last_name
            while not first_name:
                    first_name = self.get_input_data(
                        Person._meta.get_field('first_name'),
                        "User {} missing a first name. Enter a first name: ".format(user)
                    )
            while not last_name:
                last_name = self.get_input_data(
                    Person._meta.get_field('last_name'),
                    "User {} missing a last name. Enter a last name: ".format(user)
                )

            person = Person.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                nickname=user.username
            )

            if user.email:
                EmailAddress.objects.create(email_address=user.email, person=person)

            self.stdout.write("Person object created for user {}".format(user.username))

    def get_input_data(self, field, message, default=None):
        """
        Borrowed from django.contrib.auth.management.commands.createsuperuser
        """
        raw_value = input(message)
        if default and raw_value == '':
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % '; '.join(e.messages))
            val = None

        return val
