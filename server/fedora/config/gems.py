#!/usr/bin/python
"""Retrieve local ruby gem list from scripts.mit.edu

Joe Presbrey <presbrey@mit.edu"""

import commands, re, sys

def scripts_gems():
    o = commands.getoutput('gem list --local')
    return map(lambda x: len(x) > 1 and (x[0], x[1].split(', ')) or x,
               re.findall('([^\s]+)\s\(([^\)]+)\)', o))

if __name__ == "__main__":
    for x in scripts_gems():
        if x[0] == 'sources': continue
        #print >>sys.stderr, x
        for y in x[1]:
            print 'gem install %s --version %s -y' % (x[0], y)
