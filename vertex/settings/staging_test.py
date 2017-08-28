from .base import *


SECRET_KEY = get_env_variable('NOSS_STAGING_TEST_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'noss',
        'PASSWORD': get_env_variable('NOSS_TEST_PG_PASSWORD'),
        'NAME': 'noss',
        'HOST': '',  # localhost
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # faster (insecure) hasher only for tests
)

CACHES['default']['LOCATION'] = '/var/run/redis/redis.sock'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework_json_api.renderers.JSONRenderer',
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# Celery
BROKER_URL = "amqp://noss:hlgVSjikAJQTKH2muZ1L@localhost:5672/noss"

WS_AMQP_CONNECTION = {'host': 'localhost',
                      'userid': 'noss',
                      'password': 'hlgVSjikAJQTKH2muZ1L',
                      'virtual_host': 'noss_test'}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
