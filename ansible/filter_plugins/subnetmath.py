# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import netaddr

def _round_prefixes(value):
    """Takes a list of subnets, and produces a new list of subnets that are /8, /16, or /24."""
    _ret = []
    for net in netaddr.cidr_merge(netaddr.IPNetwork(v) for v in value):
        newprefix = ((net.prefixlen+7)//8)*8
        _ret.extend(net.subnet(newprefix))
    return _ret

def inaddr_zones(value):
    nets = _round_prefixes(value)
    _ret = []
    for net in nets:
        val = "in-addr.arpa"
        addr = int(net.network)
        for i in range(0, net.prefixlen, 8):
            val = str((addr >> (24-i)) & 0xff) + '.' + val
        _ret.append(val)
    return _ret

class FilterModule(object):
    def filters(self):
        return {
            'inaddr_zones': inaddr_zones,
        }
