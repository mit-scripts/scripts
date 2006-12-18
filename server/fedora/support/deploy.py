#!/usr/bin/python
"""scripts.mit.edu deployment sychronization support
Copyright (C) 2006, Joe Presbrey <presbrey@mit.edu>
"""

import sys,os,os.path as path
import string
import getopt

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
		except getopt.error, msg:
			raise Usage(msg)
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, "for help use --help"
		return 2

	for o, a in opts:
		if o in ("-h", "--help"):
			print __doc__
			return 0

if __name__ == "__main__":
	sys.exit(main())
