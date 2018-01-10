# VLANs
#
# VLANs (Virtual LANs) are a common way to create logically separate networks using the same
# physical infrastructure.
#
# Managed switches can assign VLANs to each port in either a "tagged" or an "untagged" manner. A
# VLAN is said to be "untagged" on a particular port when it is the default VLAN for that port,
# and requires no special configuration in order to access it.
#
# A "Default VLAN" is created for every fabric, to which every new VLAN-aware object in the
# fabric will be associated with by default (unless specified otherwise).
from django.db import models

from vertex.models import AbstractDatedModel


class VLAN(AbstractDatedModel):
    name = models.CharField(max_length=100)
    vlan_id = models.PositiveIntegerField()
    fabric = models.ForeignKey('ipam.Fabric')
    gateway = models.ForeignKey('ipam.IPAddress', blank=True, null=True)

    role = models.ManyToManyField('ipam.Role', blank=True)

    description = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
