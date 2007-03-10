#!/usr/bin/python
"""Retrieve local ruby gem list from scripts.mit.edu

Joe Presbrey <presbrey@mit.edu"""

import commands, re

def scripts_gems():
	cout = commands.getoutput('gem list --local')
	return re.findall('([^\s]+)\s\([0-9\.]+\)', cout)

if __name__ == "__main__":
	for x in gems_local():
		if x == 'sources': continue
		print x
