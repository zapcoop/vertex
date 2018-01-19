from datetime import datetime, timedelta

from django.conf import settings

from circuits.constants import *


def get_default_renewal_date():
  period = settings.DEFAULT_CIRCUITS_RENEWAL or RENEWAL_MONTHLY
  if period == RENEWAL_MONTHLY:
    return datetime.now() + timedelta(days=30)
  if period == RENEWAL_QUARTELY:
    return datetime.now() + timedelta(days=90)
  if period == RENEWAL_BIANNUALLY:
    return datetime.now() + timedelta(days=183)
  if period == RENEWAL_YEARLY:
    return datetime.now() + timedelta(days=365)
  if period == RENEWAL_TRIENNIALLY:
    return datetime.now() + timedelta(days=1095)
  if period == RENEWAL_QUINQUENNIALLY:
    return datetime.now() + timedelta(days=1825)