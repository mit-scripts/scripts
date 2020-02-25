# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

def permute(value, shift):
    shift %= len(value)
    return value[shift:] + value[:shift]

class FilterModule(object):
    def filters(self):
        return {
            'permute': permute,
        }
