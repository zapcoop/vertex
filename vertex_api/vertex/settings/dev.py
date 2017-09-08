from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ip5ezdgcr92+p@(o4g$kc5lzw&$-rjqf7d9-h)16(!z&(lzils'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = ('127.0.0.1', '::1',)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ('debug_toolbar',
                   'django_extensions',)

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware',] + MIDDLEWARE

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'vertex',
        'USER': 'vertex',
        'PASSWORD': '1a2e233f53edaf690',
        'HOST': '127.0.0.1',
    },
}
