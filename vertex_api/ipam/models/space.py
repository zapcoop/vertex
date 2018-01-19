# Spaces
#
# A space is a logical grouping of VLANs whose subnets are able to communicate with one another.
# VLANs within each space need not belong to the same fabric.
from django.db import models

from vertex.models import AbstractDatedModel


class Space(AbstractDatedModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name