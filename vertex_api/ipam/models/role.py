from django.db import models


class Role(models.Model):
    """
    A Role represents the functional role of a Subnet or VLAN; for example, "Customer",
    "Infrastructure", or "Management".
    """
    name = models.CharField(max_length=50, unique=True)
    weight = models.PositiveSmallIntegerField(default=1000)

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.name

    @property
    def count_prefixes(self):
        return self.subnets.count()

    @property
    def count_vlans(self):
        return self.vlans.count()
