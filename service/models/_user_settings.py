from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import VERSION

try:
    from base64 import urlsafe_b64encode as b64encode
except ImportError:
    from base64 import encodestring as b64encode
try:
    from base64 import urlsafe_b64decode as b64decode
except ImportError:
    from base64 import decodestring as b64decode


class UserSettings(models.Model):
    """
    A bunch of user-specific settings that we want to be able to define, such
    as notification preferences and other things that should probably be
    configurable.
    We should always refer to user.usersettings.settings['setting_name'].
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    settings_pickled = models.TextField(
        _('Settings Dictionary'),
        help_text=_(
            'This is a base64-encoded representation of a pickled Python dictionary. '
            'Do not change this field via the admin.'
        ),
        blank=True,
        null=True,
    )

    def _set_settings(self, data):
        # data should always be a Python dictionary.
        try:
            import pickle
        except ImportError:
            import cPickle as pickle

        self.settings_pickled = b64encode(pickle.dumps(data))

    def _get_settings(self):
        # return a python dictionary representing the pickled data.
        try:
            import pickle
        except ImportError:
            import cPickle as pickle

        try:
            return pickle.loads(b64decode(str(self.settings_pickled)))
        except pickle.UnpicklingError:
            return {}

    settings = property(_get_settings, _set_settings)

    def __str__(self):
        return u'Preferences for %s' % self.user

    class Meta:
        verbose_name = _('User Setting')
        verbose_name_plural = _('User Settings')
        app_label = 'service'


def create_usersettings(sender, instance, created, **kwargs):
    """
    Helper function to create UserSettings instances as
    required, eg when we first create the UserSettings database
    table via 'syncdb' or when we save a new user.
    If we end up with users with no UserSettings, then we get horrible
    'DoesNotExist: UserSettings matching query does not exist.' errors.
    """
    from service.settings import DEFAULT_USER_SETTINGS

    if created:
        UserSettings.objects.create(user=instance, settings=DEFAULT_USER_SETTINGS)


try:
    # Connecting via settings.AUTH_USER_MODEL (string) fails in Django < 1.7. We need the actual model there.
    # https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#referencing-the-user-model
    if VERSION < (1, 7):
        raise ValueError
    models.signals.post_save.connect(create_usersettings, sender=settings.AUTH_USER_MODEL)
except:
    signal_user = get_user_model()
    models.signals.post_save.connect(create_usersettings, sender=signal_user)