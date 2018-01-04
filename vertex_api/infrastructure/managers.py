from django.db import models

from vertex.managers import NaturalOrderByManager


class DeviceManager(NaturalOrderByManager):
    def get_queryset(self):
        return self.natural_order_by('name')

class PowerOutletManager(NaturalOrderByManager):
    def get_queryset(self):
        return self.natural_order_by('name')

