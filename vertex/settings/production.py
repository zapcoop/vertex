from .base import *

ALLOWED_HOSTS = ['.zerofail.net', '.zerofail.com']

SECRET_KEY = get_env_variable('NOSS_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'noss',
        'USER': 'noss',
        'PASSWORD': get_env_variable('NOSS_PG_PASSWORD'),
        'HOST': '127.0.0.1',
    },
}

CACHES['default']['LOCATION'] = 'redis://192.168.166.1:6380/2'

EMAIL_HOST_PASSWORD = get_env_variable('NOSS_SMTP_PASSWORD')

ALLOW_UNVERIFIED_STAFF = True
