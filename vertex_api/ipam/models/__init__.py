from django.db import models

# IP Address
# IP Range
# Subnet/Prefix
# VRF

# Fabric
# VLan
# Space

# VLAN Templates
# VLAN Group Templates

# VLAN Group


# MAC Address

# Roles

from .ip_address import IPAddress
from .ip_range import IPRangeRole, IPRange
from .subnet import Subnet
from .vrf import VRF

from .fabric import Fabric
from .vlan import VLAN
from .space import Space

from .mac_address import MACAddress

from .role import Role
