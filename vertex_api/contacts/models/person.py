from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.db import transaction
from django.core.cache import cache

from uuslug import slugify, uuslug

import reversion

from contacts.rules.organization import is_object_organization_admin

from vertex import rules
from contacts.models import EmailAddress
from vertex.rules.predicates import has_django_permission, is_staff, is_superuser
from contacts.rules.person import is_same_organization
from vertex.models import AbstractDatedModel
from . import GENERIC_INFORMATION_TYPES
from ..utils import gravatar_hash

GENDER_CHOICES = (
    ('M', _('Male')),
    ('F', _('Female')),
    ('N', _('Non-Binary')),
    ('O', _('Other')),
)


@reversion.register
class PeopleOrganizations(models.Model):
    class Meta:
        ordering = ('organization__name', 'person__full_name')
        verbose_name = _('Person Organization')
        verbose_name_plural = _('People Organizations')
        app_label = 'contacts'

    person = models.ForeignKey("contacts.Person", related_name='roles')
    organization = models.ForeignKey("contacts.Organization", related_name='people_roles')

    groups = models.ManyToManyField(
        'contacts.ContactGroup',
        verbose_name=_('groups'),
        blank=True,
        related_name='people'
    )

    role = models.CharField(max_length=150, blank=True)

    def __str__(self):
        if self.role:
            return "{person}, {role} at {org}".format(
                person=self.person.full_name,
                role=self.role,
                org=self.organization.name
            )
        else:
            return "{person} at {org}".format(
                person=self.person.full_name,
                org=self.organization.name
            )


class PersonManager(Manager):
    @transaction.atomic
    def create_person(self, first_name, last_name, email_address, organization=None, title=None,
                      middle_name=None,
                      suffix=None,
                      nickname=None):
        instance = self.create(
            title=title,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            suffix=suffix,
            nickname=nickname
        )
        instance.add_email_address(
            email_address=email_address,
            information_type='primary',
            organization=organization
        )
        return instance


@reversion.register
class Person(AbstractDatedModel):
    """Person model."""
    slug = models.SlugField(editable=False)

    title = models.CharField(
        _('Title'),
        max_length=20,
        blank=True,
        null=True
    )
    first_name = models.CharField(
        _('First name'),
        max_length=100
    )
    middle_name = models.CharField(
        _('Middle name'),
        max_length=100,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=100
    )
    suffix = models.CharField(
        _('Suffix'),
        max_length=20,
        blank=True,
        null=True)

    full_name = models.CharField(max_length=150, editable=False)

    gender = models.CharField(
        max_length=5,
        blank=True,
        choices=GENDER_CHOICES
    )

    date_of_birth = models.DateField(
        _('Date of birth'),
        blank=True,
        null=True
    )

    organizations = models.ManyToManyField(
        "contacts.Organization",
        through='contacts.PeopleOrganizations',
        blank=True
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
    )

    custom_avatar_url = models.URLField(blank=True)

    notes = models.TextField(
        blank=True,
        null=True
    )

    @cached_property
    def username(self):
        return self.user.username if self.user else None

    @cached_property
    def is_staff(self):
        return self.user.is_staff if self.user else None

    @cached_property
    def is_superuser(self):
        return self.user.is_superuser if self.user else None

    objects = PersonManager()

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name = _('Person')
        verbose_name_plural = _('People')
        app_label = 'contacts'
        permissions = (
            ('view_person', _('Can view person')),
        )

    def __str__(self):
        if self.user:
            return '{full_name} ({username})'.format(
                full_name=self.full_name,
                username=self.user.username
            )
        else:
            return self.full_name

    def clean(self):
        self.title = self.title.capitalize() if self.title else None
        self.first_name = self.first_name.capitalize() if self.first_name else None
        self.last_name = self.last_name.capitalize() if self.last_name else None
        self.suffix = self.suffix.capitalize() if self.suffix else None

    @property
    def generated_full_name(self):
        full_name = u"{first_name} {last_name}".format(
            first_name=self.first_name,
            last_name=self.last_name,
        )
        if self.suffix:
            full_name = u"{full_name}, {suffix}".format(
                full_name=full_name,
                suffix=self.suffix
            )
        if self.title:
            full_name = u"{title} {full_name}".format(
                title=self.title,
                full_name=full_name
            )
        return full_name

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        if self.user and not keep_parents:
            self.user.groups.clear()
            self.user.active = False
            self.user.save()

        super(Person, self).delete(using, keep_parents)

    def save(self, *args, **kwargs):
        if self.pk is not None and self.user:
            user_obj = self.user
            prev_obj = Person.objects.get(pk=self.pk)
            if self.first_name != prev_obj.first_name or self.last_name != prev_obj.last_name:
                user_obj.first_name = self.first_name
                user_obj.last_name = self.last_name
                user_obj.save()

        if self.full_name != self.generated_full_name:
            self.full_name = self.generated_full_name

        if not self.slug:
            self.slug = uuslug(self.full_name, instance=self)

        super(Person, self).save(*args, **kwargs)

    def add_email_address(self, email_address, information_type=None, organization=None):
        """
        Add an email address for this person.
        :param email_address: the email address to add, as a string
        :param information_type: must be in GENERIC_INFORMATION_TYPES if given.
        :param organization: the email will also be associated to `organization`. if `None`,
            will try to infer it from the email domain. If the organization can't be inferred from
            the email domain, the email address won't be associated with an organization.
        :return the created EmailAdress object
        """
        if information_type is not None and information_type not in dict(GENERIC_INFORMATION_TYPES):
            raise Exception('Invalid information_type')
        kwargs = {
            'email_address': email_address,
            'person': self,
            'organization': organization
        }
        if information_type is not None:
            kwargs['information_type'] = information_type
        return EmailAddress.objects.create(**kwargs)

    @transaction.atomic
    def set_primary_email(self, email_address):
        cache.delete('{app}_{model}_{name}_{id}'.format(
            app=self._meta.app_label,
            model=self._meta.model_name,
            name='gravatar_url',
            id=self.pk
        ))

        emails = self.email_addresses.select_for_update().all()
        email_address.refresh_from_db()
        if email_address.person == self:
            if self.user:
                self.user.email = email_address.email_address
                self.user.save()
            email_address.primary = True
            email_address.save()
            emails.exclude(pk=email_address.pk).update(primary=False)

    @cached_property
    def primary_email(self):
        return self.email_addresses.filter(primary=True).first()

    @property
    def gravatar_url(self):
        hash_input = getattr(self.primary_email, 'email_address', self.pk)
        hashvalue = gravatar_hash(hash_input)
        return 'https://secure.gravatar.com/avatar/{}'.format(hashvalue)

    @transaction.atomic
    def create_login(self, **user_kwargs):
        if not self.primary_email:
            email = self.email_addresses.first()
            if email:
                self.set_primary_email(email)
                user_kwargs['email'] = email.email_address
        self.user = User.objects.create(**user_kwargs)
        self.save()
        return self.user


rules.add_perm('contacts.view_person', is_superuser | is_staff | is_same_organization)
rules.add_perm('contacts.add_person',
               is_superuser | is_object_organization_admin | is_staff & has_django_permission(
                   'contacts.add_person'))
rules.add_perm('contacts.change_person',
               is_superuser | is_object_organization_admin | is_staff & has_django_permission(
                   'contacts.change_person'))
rules.add_perm('contacts.delete_person',
               is_superuser | is_object_organization_admin | is_staff & has_django_permission(
                   'contacts.delete_person'))
