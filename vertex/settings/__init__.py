DEFAULT_APP_SETTINGS = {
    'ALLOW_UNVERIFIED_STAFF': False,
    'DNS_NOTIFY_PAGE_SIZE': 100
}


class AppSettings(object):

    @property
    def django_settings(self):
        if not hasattr(self, '_django_settings'):
            from django.conf import settings
            self._django_settings = settings
        return self._django_settings

    def __getattr__(self, attr):
        if attr not in DEFAULT_APP_SETTINGS.keys():
            raise AttributeError('Invalid app setting: {}'.format(attr))
        if hasattr(self.django_settings, 'APP_' + attr):
            return getattr(self.django_settings, 'APP_' + attr)
        else:
            return DEFAULT_APP_SETTINGS[attr]


app_settings = AppSettings()
