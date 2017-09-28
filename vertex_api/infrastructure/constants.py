# Parent/child device roles
SUBDEVICE_ROLE_PARENT = True
SUBDEVICE_ROLE_CHILD = False
SUBDEVICE_ROLE_CHOICES = (
    (None, 'None'),
    (SUBDEVICE_ROLE_PARENT, 'Parent'),
    (SUBDEVICE_ROLE_CHILD, 'Child'),
)

# Interface ordering schemes (for device types)
IFACE_ORDERING_POSITION = 1
IFACE_ORDERING_NAME = 2
IFACE_ORDERING_CHOICES = [
    [IFACE_ORDERING_POSITION, 'Slot/position'],
    [IFACE_ORDERING_NAME, 'Name (alphabetically)']
]

# Interface form factors
# Virtual
IFACE_FF_VIRTUAL = 0
IFACE_FF_LAG = 200
# Ethernet
IFACE_FF_100ME_FIXED = 800
IFACE_FF_1GE_FIXED = 1000
IFACE_FF_1GE_GBIC = 1050
IFACE_FF_1GE_SFP = 1100
IFACE_FF_10GE_FIXED = 1150
IFACE_FF_10GE_CX4 = 1170
IFACE_FF_10GE_SFP_PLUS = 1200
IFACE_FF_10GE_XFP = 1300
IFACE_FF_10GE_XENPAK = 1310
IFACE_FF_10GE_X2 = 1320
IFACE_FF_25GE_SFP28 = 1350
IFACE_FF_40GE_QSFP_PLUS = 1400
IFACE_FF_100GE_CFP = 1500
IFACE_FF_100GE_QSFP28 = 1600
# Wireless
IFACE_FF_80211A = 2600
IFACE_FF_80211G = 2610
IFACE_FF_80211N = 2620
IFACE_FF_80211AC = 2630
IFACE_FF_80211AD = 2640
# Fibrechannel
IFACE_FF_1GFC_SFP = 3010
IFACE_FF_2GFC_SFP = 3020
IFACE_FF_4GFC_SFP = 3040
IFACE_FF_8GFC_SFP_PLUS = 3080
IFACE_FF_16GFC_SFP_PLUS = 3160
# Serial
IFACE_FF_T1 = 4000
IFACE_FF_E1 = 4010
IFACE_FF_T3 = 4040
IFACE_FF_E3 = 4050
# Stacking
IFACE_FF_STACKWISE = 5000
IFACE_FF_STACKWISE_PLUS = 5050
IFACE_FF_FLEXSTACK = 5100
IFACE_FF_FLEXSTACK_PLUS = 5150
IFACE_FF_JUNIPER_VCP = 5200
# Other
IFACE_FF_OTHER = 32767

IFACE_FF_CHOICES = [
    [
        'Virtual interfaces',
        [
            [IFACE_FF_VIRTUAL, 'Virtual'],
            [IFACE_FF_LAG, 'Link Aggregation Group (LAG)'],
        ]
    ],
    [
        'Ethernet (fixed)',
        [
            [IFACE_FF_100ME_FIXED, '100BASE-TX (10/100ME)'],
            [IFACE_FF_1GE_FIXED, '1000BASE-T (1GE)'],
            [IFACE_FF_10GE_FIXED, '10GBASE-T (10GE)'],
            [IFACE_FF_10GE_CX4, '10GBASE-CX4 (10GE)'],
        ]
    ],
    [
        'Ethernet (modular)',
        [
            [IFACE_FF_1GE_GBIC, 'GBIC (1GE)'],
            [IFACE_FF_1GE_SFP, 'SFP (1GE)'],
            [IFACE_FF_10GE_SFP_PLUS, 'SFP+ (10GE)'],
            [IFACE_FF_10GE_XFP, 'XFP (10GE)'],
            [IFACE_FF_10GE_XENPAK, 'XENPAK (10GE)'],
            [IFACE_FF_10GE_X2, 'X2 (10GE)'],
            [IFACE_FF_25GE_SFP28, 'SFP28 (25GE)'],
            [IFACE_FF_40GE_QSFP_PLUS, 'QSFP+ (40GE)'],
            [IFACE_FF_100GE_CFP, 'CFP (100GE)'],
            [IFACE_FF_100GE_QSFP28, 'QSFP28 (100GE)'],
        ]
    ],
    [
        'Wireless',
        [
            [IFACE_FF_80211A, 'IEEE 802.11a'],
            [IFACE_FF_80211G, 'IEEE 802.11b/g'],
            [IFACE_FF_80211N, 'IEEE 802.11n'],
            [IFACE_FF_80211AC, 'IEEE 802.11ac'],
            [IFACE_FF_80211AD, 'IEEE 802.11ad'],
        ]
    ],
    [
        'FibreChannel',
        [
            [IFACE_FF_1GFC_SFP, 'SFP (1GFC)'],
            [IFACE_FF_2GFC_SFP, 'SFP (2GFC)'],
            [IFACE_FF_4GFC_SFP, 'SFP (4GFC)'],
            [IFACE_FF_8GFC_SFP_PLUS, 'SFP+ (8GFC)'],
            [IFACE_FF_16GFC_SFP_PLUS, 'SFP+ (16GFC)'],
        ]
    ],
    [
        'Serial',
        [
            [IFACE_FF_T1, 'T1 (1.544 Mbps)'],
            [IFACE_FF_E1, 'E1 (2.048 Mbps)'],
            [IFACE_FF_T3, 'T3 (45 Mbps)'],
            [IFACE_FF_E3, 'E3 (34 Mbps)'],
        ]
    ],
    [
        'Stacking',
        [
            [IFACE_FF_STACKWISE, 'Cisco StackWise'],
            [IFACE_FF_STACKWISE_PLUS, 'Cisco StackWise Plus'],
            [IFACE_FF_FLEXSTACK, 'Cisco FlexStack'],
            [IFACE_FF_FLEXSTACK_PLUS, 'Cisco FlexStack Plus'],
            [IFACE_FF_JUNIPER_VCP, 'Juniper VCP'],
        ]
    ],
    [
        'Other',
        [
            [IFACE_FF_OTHER, 'Other'],
        ]
    ],
]

VIRTUAL_IFACE_TYPES = [
    IFACE_FF_VIRTUAL,
    IFACE_FF_LAG,
]

WIRELESS_IFACE_TYPES = [
    IFACE_FF_80211A,
    IFACE_FF_80211G,
    IFACE_FF_80211N,
    IFACE_FF_80211AC,
    IFACE_FF_80211AD,
]

NONCONNECTABLE_IFACE_TYPES = VIRTUAL_IFACE_TYPES + WIRELESS_IFACE_TYPES

# Device statuses
STATUS_OFFLINE = 0
STATUS_ACTIVE = 1
STATUS_PLANNED = 2
STATUS_STAGED = 3
STATUS_FAILED = 4
STATUS_INVENTORY = 5
STATUS_CHOICES = [
    [STATUS_ACTIVE, 'Active'],
    [STATUS_OFFLINE, 'Offline'],
    [STATUS_PLANNED, 'Planned'],
    [STATUS_STAGED, 'Staged'],
    [STATUS_FAILED, 'Failed'],
    [STATUS_INVENTORY, 'Inventory'],
]

# Bootstrap CSS classes for device stasuses
DEVICE_STATUS_CLASSES = {
    0: 'warning',
    1: 'success',
    2: 'info',
    3: 'primary',
    4: 'danger',
    5: 'default',
}

# Console/power/interface connection statuses
CONNECTION_STATUS_PLANNED = False
CONNECTION_STATUS_CONNECTED = True
CONNECTION_STATUS_CHOICES = [
    [CONNECTION_STATUS_PLANNED, 'Planned'],
    [CONNECTION_STATUS_CONNECTED, 'Connected'],
]

# Platform -> RPC client mappings
RPC_CLIENT_JUNIPER_JUNOS = 'juniper-junos'
RPC_CLIENT_CISCO_IOS = 'cisco-ios'
RPC_CLIENT_OPENGEAR = 'opengear'
RPC_CLIENT_CHOICES = [
    [RPC_CLIENT_JUNIPER_JUNOS, 'Juniper Junos (NETCONF)'],
    [RPC_CLIENT_CISCO_IOS, 'Cisco IOS (SSH)'],
    [RPC_CLIENT_OPENGEAR, 'Opengear (SSH)'],
]