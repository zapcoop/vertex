from .base import *

SECRET_KEY = 'ip5ezdgcr92+p@(o4g$kc5lzw&$-rjqf7d9-h)16(!z&(lzils'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # faster (insecure) hasher only for tests
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'noss',
        'USER': 'noss',
        'PASSWORD': '1a2e233f53edaf690',
        'HOST': '127.0.0.1',
    },
}

CACHES['default']['LOCATION'] = '/var/run/redis/redis.sock?db=1'

BROKER_URL = "amqp://noss:hlgVSjikAJQTKH2muZ1L@localhost:5672/noss"

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

WS_AMQP_CONNECTION = {'host': 'localhost',
                      'userid': 'noss',
                      'password': 'hlgVSjikAJQTKH2muZ1L',
                      'virtual_host': 'noss_test'}
