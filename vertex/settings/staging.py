from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ip5ezdgcr92+p@(o4g$kc5lzw&$-rjqf7d9-h)16(!z&(lzils'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '.zerofail.com', '.zerofail.net', '192.168.166.232', '208.85.113.12']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'staging',
        'USER': 'staging',
        'PASSWORD': '1a2e233f53edaf690',
        'HOST': '192.168.166.110',
    },
}

CACHES['default']['LOCATION'] = 'redis://192.168.166.1:6380/3'

JWT_AUTH['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=259200)

EMAIL_HOST = 'relay.zerofail.com'

STATIC_ROOT = '/opt/noss/static'

ADMINS = (
    ('Jonathan Senecal', 'jsenecal@zerofail.com'),
    ('Leifur Halldor Asgeirsson', 'lasgeirsson@zerofail.com'),
)

APP_ALLOW_UNVERIFIED_STAFF = True


# Celery
BROKER_URL = "amqp://noss:hlgVSjikAJQTKH2muZ1L@localhost:5672/noss"

WS_AMQP_CONNECTION = {'host': 'localhost',
                      'userid': 'noss',
                      'password': 'hlgVSjikAJQTKH2muZ1L',
                      'virtual_host': 'noss'}