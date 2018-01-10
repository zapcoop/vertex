# Fabrics
#
# A fabric could be described as a VLAN namespace mechanism. It's a switch or a combination of
# switches that use trunking to provide the same VLANs.
from django.db import models

from vertex.models import AbstractDatedModel


class Fabric(AbstractDatedModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
