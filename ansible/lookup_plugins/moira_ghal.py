from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
lookup: moira_ghal
description:
- This lookup returns the aliases of a Moira host.
"""

import subprocess

from ansible.module_utils._text import to_text
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()

DOMAIN = ".mit.edu"

class LookupModule(LookupBase):
    def ghal(self, host):
        p = subprocess.Popen(
            ["qy", "-n", "-s", "ghal", "*", host],
            cwd=self._loader.get_basedir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if stderr:
            display.warning("qy: %s" % stderr)
        return [s.split(',', 2)[0].lower() for s in to_text(stdout).splitlines()]
    def run(self, terms, include_short_names=False, include_cname=False, **kwargs):
        ret = []
        for host in sorted(set(host.lower() for host in terms)):
            display.debug("Looking up aliases for: %s" % host)
            aliases = self.ghal(host)
            if include_cname:
                aliases.insert(0, host)
            ret.extend(aliases)
            if include_short_names:
                for h in aliases:
                    if h.endswith(DOMAIN):
                        aliases.append(h[:-len(DOMAIN)])
        return ret
