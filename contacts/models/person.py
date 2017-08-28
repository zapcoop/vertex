from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.db import transaction
from django.core.cache import cache
import reversion

from contacts.rules.organization import is_object_organization_admin

from noss import rules
from contacts.models import EmailAddress
from noss.rules.predicates import has_django_permission, is_staff, is_superuser
from contacts.rules.person import is_same_organization
from noss.models import AbstractDatedModel, AbstractSelfUpdatingModel
from . import GENERIC_INFORMATION_TYPES
from noss.utils.softdeletion import SoftDeletableModel, SoftDeletableManager
from noss.utils import cache_result
from ..utils import gravatar_hash

GENDER_CHOICES = (
    ('M', _('Male')),
    ('F', _('Female')),
    ('O', _('Other')),
)


class PersonManager(SoftDeletableManager):
    @transaction.atomic
    def create_person(self, first_name, last_name, email_address, organization=None, title=None, middle_name=None,
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
class Person(AbstractSelfUpdatingModel, SoftDeletableModel, AbstractDatedModel):
    """Person model."""
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
    nickname = models.CharField(
        _('Nickname'),
        max_length=20,
        blank=True,
        null=True
    )

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

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
    )

    custom_avatar_url = models.URLField(blank=True)

    @property
    def username(self):
        return self.user.username if self.user else None

    @property
    def is_staff(self):
        return self.user.is_staff if self.user else None

    @property
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
        if not self.slug:
            self.slug = slugify(self.full_name)

        self.title = self.title.capitalize()
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        self.suffix = self.suffix.capitalize()

    @property
    def full_name(self):
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
    def delete(self, force=False):
        if self.user and not force:
                self.user.groups.clear()
                self.user.active = False
                self.user.save()

        super(Person, self).delete(force=force)

    def save(self, *args, **kwargs):
        if self.pk is not None and self.user:
            user_obj = self.user
            prev_obj = Person.objects.get(pk=self.pk)
            if self.first_name != prev_obj.first_name or self.last_name != prev_obj.last_name:
                user_obj.first_name = self.first_name
                user_obj.last_name = self.last_name
                user_obj.save()
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
    @cache_result(timeout=None)
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
               is_superuser | is_object_organization_admin | is_staff & has_django_permission('contacts.add_person'))
rules.add_perm('contacts.change_person',
               is_superuser | is_object_organization_admin | is_staff & has_django_permission('contacts.change_person'))
rules.add_perm('contacts.delete_person',
               is_superuser | is_object_organization_admin | is_staff & has_django_permission('contacts.delete_person'))
