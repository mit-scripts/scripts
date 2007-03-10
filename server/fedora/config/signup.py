#!/usr/bin/python
"""Add system users from external passwd and group files
Joe Presbrey <presbrey@mit.edu>

arguments: <passwd-file> <group-file>"""


import commands
import os,sys,string
#import athena

def do_groupfile(f):
	for x in f.readlines():
		gname = x.strip().split(':')[0]
		gid = x.strip().split(':')[2]
		c = commands.getstatusoutput('groupadd -g ' + gid + ' ' + gname)
		if c[0] == 0:
			print "group " + gname + "/" + gid + " added successfully."

def do_userfile(f):
	for x in f.readlines():
		name = x.strip().split(':')[0]
		#uathena = AthenaUser(name)
		uid = x.strip().split(':')[2]
		gid = x.strip().split(':')[3]
		home = x.strip().split(':')[5]
		if uid > 100:
			c = commands.getstatusoutput('useradd -M -d ' + home + ' -u ' + uid + ' -g ' + gid + ' -G users -s /usr/local/bin/mbash ' + name)
			if c[0] == 0:
				print "user " + name + "/" + uid + " added successfully."

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print __doc__
	else:
		do_groupfile(file(sys.argv[2]))
		do_userfile(file(sys.argv[1]))
