from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Subnet, Space, IPAddress

ROOT_PARENT_MUST_BE_NONE = 'Subnet {0} has a parent but should be a root'
CHILD_WRONG_PARENT = 'Subnet {0} : wrong parent! Expected: {1}, was: {2}'
CHILD_PARENT_IS_NONE = 'Subnet {0} : should be a child, but has parent None'
SUPERNET_CONFLICT = 'Subnet {0} : Stored supernet {1} conflicts with result of find_parent {2}'


class SubnetsAndAddressesTests(TestCase):

    def setUp(self):
        Space.objects.get_or_create(name="Test Space", pk=1)

        Subnet.objects.get_or_create(cidr=IPNetwork('172.16.0.0/16'))
        Subnet.objects.get_or_create(cidr=IPNetwork('172.16.0.0/24'))

        Subnet.objects.get_or_create(cidr='10.0.0.0/8')
        Subnet.objects.get_or_create(cidr='10.1.0.0/16')
        Subnet.objects.get_or_create(cidr='10.2.0.0/16')
        Subnet.objects.get_or_create(cidr='10.2.0.0/24')
        Subnet.objects.get_or_create(cidr='10.2.1.0/24')
        Subnet.objects.get_or_create(cidr='10.2.3.0/24')
        Subnet.objects.get_or_create(cidr='10.2.0.0/30')
        Subnet.objects.get_or_create(cidr='10.2.0.4/30')
        Subnet.objects.get_or_create(cidr='10.2.3.4/30')
        Subnet.objects.get_or_create(cidr='10.4.0.0/24')
        Subnet.objects.get_or_create(cidr='10.4.3.0/24')

        IPAddress.objects.get_or_create(address='10.2.3.1')
        IPAddress.objects.get_or_create(address='10.2.3.2')

        Subnet.objects.get_or_create(cidr='2001:db8:abcd:12::/64')
        Subnet.objects.get_or_create(cidr='2001:db8:abcd:12::/80')

        IPAddress.objects.get_or_create(address='2001:db8:abcd:12::1')


    def tearDown(self):
        print(Subnet.objects.order_by('cidr'))
        for subnet in Subnet.objects.all():
            self.assertEqual(
                subnet.supernet,
                subnet.find_parent(),
                SUPERNET_CONFLICT.format(subnet, subnet.supernet, subnet.find_parent())
            )

    def test_new_root(self):
        new_root1, created = Subnet.objects.get_or_create(cidr='192.0.0.0/8')
        new_root2, created = Subnet.objects.get_or_create(cidr='193.0.0.0/8')

        self.assertIsNone(new_root1.supernet, ROOT_PARENT_MUST_BE_NONE.format(str(new_root1)))
        self.assertIsNone(new_root2.supernet, ROOT_PARENT_MUST_BE_NONE.format(str(new_root2)))

    def test_new_child(self):
        new_root, created = Subnet.objects.get_or_create(cidr='192.0.0.0/8')
        new_child1, created = Subnet.objects.get_or_create(cidr='192.1.0.0/16')

        self.assertEqual(new_child1.supernet, new_root,
                         CHILD_WRONG_PARENT.format(str(new_child1), str(new_root), str(new_child1.supernet)))

    def test_new_child_with_multiple_ancestors(self):
        Subnet.objects.get_or_create(cidr='192.0.0.0/8')
        p, created = Subnet.objects.get_or_create(cidr='192.1.0.0/16')
        s, created = Subnet.objects.get_or_create(cidr='192.1.1.0/24')

        self.assertEqual(
            s.supernet,
            p,
            CHILD_WRONG_PARENT.format(str(s), str(p), str(s.supernet)))

    def test_remove_leafnode(self):
        leaf = Subnet.objects.get(cidr='10.2.3.4/30')
        leaf.delete()
        self.assertEqual(Subnet.objects.filter(cidr='10.2.3.4/30').count(), 0, 'Deletion failed!')

    def test_remove_internal_node(self):
        initial_total_subnets = Subnet.objects.count()
        node = Subnet.objects.get(cidr='10.2.0.0/24')
        node.delete()
        self.assertEqual(
            Subnet.objects.filter(cidr='10.2.0.0/24').count(),
            0,
            'Deletion failed!'
        )
        self.assertTrue(
            Subnet.objects.all().count() == initial_total_subnets - 1,
            'Deletion failed!'
        )

    def test_laterally_move_leafnode(self):
        old_cidr = '10.2.3.4/30'
        new_cidr= '10.2.1.4/30'
        old_parent = '10.2.3.0/24'
        new_parent = '10.2.1.0/24'

        node = Subnet.objects.get(cidr=old_cidr)
        node.cidr = new_cidr
        node.save()
        self.assertEqual(
            Subnet.objects.get(cidr=new_cidr).supernet,
            Subnet.objects.get(cidr=new_parent),
            CHILD_WRONG_PARENT.format(
                Subnet.objects.get(cidr=new_cidr),
                Subnet.objects.get(cidr=new_parent),
                Subnet.objects.get(cidr=new_cidr).supernet
            )
        )
        self.assertEqual(
            Subnet.objects.get(cidr=new_cidr).children.count(),
            0,
            "leaf node shouldn't have children"
        )
        self.assertEqual(
            Subnet.objects.filter(cidr=old_cidr).count(),
            0,
            'old cidr still exists after move'
        )

    def test_laterally_move_internal_node_noresize(self):
        old_cidr = '10.2.0.0/16'
        new_cidr = '10.3.0.0/16'

        node = Subnet.objects.get(cidr=old_cidr)

        node.cidr = new_cidr
        node.save()

        self.assertEqual(
            Subnet.objects.filter(cidr=old_cidr).count(),
            0,
            'old cidr still exists after move'
        )

    def test_vertically_move_node(self):
        old_cidr = '10.2.0.0/24'
        new_cidr = '10.4.0.0/16'

        node = Subnet.objects.get(cidr=old_cidr)
        node.cidr = new_cidr
        node.save()

        self.assertEqual(
            Subnet.objects.filter(cidr=old_cidr).count(),
            0,
            'old cidr still exists after move'
        )

    def test_get_direct_children(self):
        expected = ['10.2.0.0/24', '10.2.1.0/24', '10.2.3.0/24']
        subnet = Subnet.objects.get(cidr='10.2.0.0/16')

        self.assertQuerysetEqual(
            subnet.get_direct_children_subnets_from_cidr(),
            expected,
            ordered=False,
            transform=lambda s: str(s.cidr)
        )

    def test_ip_address_no_parent(self):
        with self.assertRaises(ValueError):
            address, created = IPAddress.objects.get_or_create(address='172.31.3.1')

    def test_ip_address_conflicting_with_subnet(self):
        with self.assertRaises(ValueError):
            address, created = IPAddress.objects.get_or_create(address='10.2.0.4')
            pass