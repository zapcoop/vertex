from django.db import transaction
from netfields import NetManager

from ipam.models import IPAddress


class SubnetManager(NetManager):

    def cleanup_and_delete(self, obj):
        with transaction.atomic():
            self.get_queryset().filter(supernet=obj).update(supernet=obj.supernet)
            IPAddress.objects.filter(subnet=obj).update(subnet=obj.supernet)
            obj.delete()

    def subnet_descendants(self, cidr):
        return self.get_queryset().filter(cidr__net_contained=cidr)
