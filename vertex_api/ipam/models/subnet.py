from django.db import models, transaction
from django.core.cache import cache
import netaddr

from netfields import CidrAddressField

from ipam.constants import AV_CHOICES
from ipam.managers import SubnetManager


# Subnets
#
# A subnet is a "layer 3" network. It is defined by a network address and a network mask length
# (in bits) and is usually written in "CIDR" format. Vertex supports IPv4 and IPv6 subnets.

class Subnet(models.Model):
    """
    A Subnet represents an IPv4 or IPv6 network, including mask length. Subnets can
    be assigned to Spaces and VRFs.
    A Subnet must be assigned a status and may optionally be assigned a used-defined
    Role. A Subnet can also be assigned to a VLAN where appropriate.
    """

    objects = SubnetManager()

    name = models.CharField(max_length=50)
    cidr = CidrAddressField(unique=True)

    supernet = models.ForeignKey(
        'self',
        related_name='children',
        null=True,
        db_index=True,
        editable=False
    )

    version = models.PositiveSmallIntegerField(choices=AV_CHOICES, editable=False)

    vrf = models.ForeignKey('ipam.VRF', blank=True, null=True)

    space = models.ForeignKey('ipam.Space', default=1)
    vlan = models.ForeignKey('ipam.VLAN', blank=True, null=True)

    role = models.ManyToManyField('ipam.Role', blank=True)

    description = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def get_direct_children_subnets_from_cidr(self):
        descendants = Subnet.objects.subnet_descendants(cidr=self.cidr).order_by('cidr')

        if not descendants:
            return descendants

        roots = [descendants.first()]
        root = roots[0]

        for subnet in descendants[1:]:
            if not subnet.cidr.overlaps(root.cidr):
                roots.append(subnet)
                root = subnet

        return Subnet.objects.filter(pk__in=[root.pk for root in roots])

    def save(self, *args, **kwargs):
        if cache.get('display_with_ancestors'):
            cache.delete('display_with_ancestors')

        if not isinstance(self.cidr, netaddr.IPNetwork):
            self.cidr = netaddr.IPNetwork(self.cidr)

        self.version = self.cidr.version

        if not self.pk:  # this is a new instance
            self.supernet = self.find_parent()

            with transaction.atomic():
                super(Subnet, self).save(*args, **kwargs)
                self.get_direct_children_subnets_from_cidr().update(supernet=self)


        else:  # instance is being updated
            old_parent = self.supernet
            self.supernet = self.find_parent()

            with transaction.atomic():
                self.children.update(supernet=old_parent)
                super(Subnet, self).save(*args, **kwargs)
                self.get_direct_children_subnets_from_cidr().update(supernet=self)

    def delete(self, *args, **kwargs):
        if self.children.count() > 0:  # if we need to repair the tree, let SubnetManager deal
            # with it
            Subnet.objects.cleanup_and_delete(self)
        else:
            super(Subnet, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.cidr)

    def find_parent(self):
        enclosing_subnets = Subnet.objects.filter(cidr__net_contains=self.cidr).order_by('-cidr')
        return enclosing_subnets.first()

    @classmethod
    def _update_display_with_ancestors_cache(cls):
        results = dict()
        for subnet in Subnet.objects.all():
            results[subnet.id] = subnet._display_with_ancestors()

        cache.set('display_with_ancestors', results, timeout=None)

    def display_with_ancestors(self):
        cached_values = cache.get('display_with_ancestors')
        if cached_values:
            return cached_values[self.id]
        else:
            Subnet._update_display_with_ancestors_cache()
            return cache.get('display_with_ancestors')[self.id]

    def _display_with_ancestors(self):
        s = list()
        parent = self.supernet
        while parent is not None:
            s.append(str(parent))
            parent = parent.supernet
        s.reverse()
        s.append(str(self))
        return ' > '.join(s)
