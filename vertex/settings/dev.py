from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ip5ezdgcr92+p@(o4g$kc5lzw&$-rjqf7d9-h)16(!z&(lzils'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = ('127.0.0.1', '::1',)

ALLOWED_HOSTS = ['127.0.0.1']

INSTALLED_APPS += ('debug_toolbar',
                   'django_extensions',)

MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'noss',
        'USER': 'noss',
        'PASSWORD': '1a2e233f53edaf690',
        'HOST': '127.0.0.1',
    },
}

CACHES['default']['LOCATION'] = '/var/run/redis/redis.sock'

JWT_AUTH['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=259200)
JWT_AUTH['JWT_ALGORITHM'] = 'HS256'


EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = 'lmail'
EMAIL_HOST_PASSWORD = 'badpassword'


# Celery
BROKER_URL = "amqp://noss:hlgVSjikAJQTKH2muZ1L@localhost:5672/noss"

APP_ALLOW_UNVERIFIED_STAFF = True

WS_AMQP_CONNECTION = {'host': 'localhost',
                      'userid': 'noss',
                      'password': 'hlgVSjikAJQTKH2muZ1L',
                      'virtual_host': 'noss'}

