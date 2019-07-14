# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import netaddr
from itertools import groupby

def _round_prefixes(value):
    """Takes a list of subnets, and produces a new list of subnets that are /8, /16, or /24."""
    _ret = []
    for net in netaddr.cidr_merge(netaddr.IPNetwork(v) for v in value):
        newprefix = ((net.prefixlen+7)//8)*8
        _ret.extend(net.subnet(newprefix))
    return _ret

def inaddr_zones(value):
    """inaddr_zones converts a list of IP subnets into a list of in-addr.arpa zone names that cover the subents."""
    nets = _round_prefixes(value)
    _ret = []
    for net in nets:
        val = "in-addr.arpa"
        addr = int(net.network)
        for i in range(0, net.prefixlen, 8):
            val = str((addr >> (24-i)) & 0xff) + '.' + val
        _ret.append(val)
    return _ret

def ipsubnets_regex(value):
    """ipsubnets_regex converts a list of IP subnets into a regex that matches IP addresses on those subnets."""
    nets = _round_prefixes(value)
    prefixes = [net.network.ipv4().format().split('.')[:net.prefixlen//8] for net in nets]
    return '^' + _prefixes_to_regex(prefixes) + r'\.'

def _prefixes_to_regex(prefixes):
    """
    Convert a list of tuples containing IP prefixes into a regex that matches them.

    Args:
      prefixes: list of prefixes like [(10,), (18, 1), (18, 2)]

    Returns:
      regex like "(10|18\.[1-2])"
    """
    out = []
    if max(len(x) for x in prefixes) == 1:
        # Last component, try to use character classes
        return _numbers_regex(x[0] for x in prefixes)
    for octet, g in groupby(prefixes, lambda x: x[0]):
        sub = [x[1:] for x in g if len(x) > 1]
        match = str(octet)
        if sub:
            match += r'\.' + _prefixes_to_regex(sub)
        out.append(match)
    return '(' + '|'.join(out) + ')'

def _numbers_regex(numbers):
    """Find a simplified regex for matching a list of numbers"""
    def key(x): return (x[0], len(x[1]), x[1][:-1])
    numbers = sorted((('', str(x)) for x in numbers), key=key)
    simplified = False
    while not simplified:
        simplified = True
        out = []
        for (suffix, _, prefix), g in groupby(numbers, key):
            g = list(g)
            if len(g) == 1 and not g[0][1]:
                out.append(g[0])
                continue
            simplified = False
            digits = sorted(x[1][-1] for x in g)
            if len(digits) == 1:
                match = digits[0]
            elif len(digits) == 10:
                match = r'\d'
            else:
                match = '['+''.join(digits)+']'
            out.append((match+suffix, prefix))
        numbers = out
    if len(numbers) == 1:
        return numbers[0][0]
    return '('+ '|'.join(x[0] for x in numbers) + ')'

class FilterModule(object):
    def filters(self):
        return {
            'inaddr_zones': inaddr_zones,
            'ipsubnets_regex': ipsubnets_regex,
        }
