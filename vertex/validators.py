from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def target_validator(value):
    if not is_target(value):
        raise ValidationError(_('Invalid target'))
    return value


def is_target(v):
    """
    Check value is valid Route Distinguisher

    Special case target: "" (empty string)
    >>> is_target("")
    True

    Type 0 RD: <2byte ASN> : <ID>

    >>> is_target("100:10")
    True
    >>> is_target("100:0")
    True
    >>> is_target("100:4294967295")
    True
    >>> is_target("0:-10")
    False
    >>> is_target("0:4294967296")
    False

    Type 1 RD: <IPv4> : <ID>

    >>> is_target("10.10.10.10:0")
    True
    >>> is_target("10.10.10.10:65535")
    True
    >>> is_target("10.10.10.10:-1")
    False
    >>> is_target("10.10.10.10:65536")
    False

    Type 2 RD: <4byte ASN> : <ID>

    >>> is_target("100000:0")
    True
    >>> is_target("100000:65535")
    True

    Error handling

    >>> is_target("100000:-1")
    False
    >>> is_target("100000:65536")
    False
    >>> is_target("10:20:30")
    False
    >>> is_target("100:b")
    False
    """
    if v == "":
        return True
    x = v.split(":")
    if len(x) != 2:
        return False
    a, b = x
    try:
        b = int(b)
    except ValueError:
        return False
    if is_asn(a):
        a = int(a)
        if a <= 65535:
            # Type 0 RD: <2byte ASN>: <ID>
            return 0 <= b <= 4294967295
        # Type 2 RD: <4 byte ASN>: <ID>
        return 0 <= b <= 65535
    if is_ipv4(a):
        # Type 1 RD: <ipv4>:<ID>
        return 0 <= b <= 65535
    return False


def is_asn(v):
    """
    Check value is valid 2-byte or 4-byte autonomous system number

    >>> is_asn(100)
    True
    >>> is_asn(100000)
    True
    >>> is_asn(-1)
    False
    """
    try:
        v = int(v)
        return v > 0
    except ValueError:
        return False


def is_ipv4(v):
    """
    Check value is valid IPv4 address

    >>> is_ipv4("192.168.0.1")
    True
    >>> is_ipv4("192.168.0")
    False
    >>> is_ipv4("192.168.0.1.1")
    False
    >>> is_ipv4("192.168.1.256")
    False
    >>> is_ipv4("192.168.a.250")
    False
    """
    X = v.split(".")
    if len(X) != 4:
        return False
    try:
        return len([x for x in X if 0 <= int(x) <= 255]) == 4
    except:
        return False
