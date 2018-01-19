from django.db import models


class ManufacturerManager(models.Manager):
    def get_queryset(self):
        return super(ManufacturerManager, self).get_queryset().filter(groups=1)


class TelecomProviderManager(models.Manager):
    def get_queryset(self):
        return super(TelecomProviderManager, self).get_queryset().filter(groups=2)


class HardwareSupplierManager(models.Manager):
    def get_queryset(self):
        return super(HardwareSupplierManager, self).get_queryset().filter(groups=3)
