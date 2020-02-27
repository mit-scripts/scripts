#!/usr/bin/python

import sys
import subprocess
import re
import socket

# Ignore the input from the finger protocol
sys.stdin.readline()

lines = subprocess.check_output(['/sbin/ipvsadm', '-L', '-n']).split(b'\n')
realserver = re.compile('(  -> )([^:]*):([^ ]*) *(.*)$')
ipaddress = re.compile('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
for line in lines:
    line = line.decode('utf8')
    realline = realserver.match(line)
    if realline:
        (preamble, ip, port, rest) = realline.groups()
        target = ip
        if ipaddress.match(ip):
            try:
                target = socket.gethostbyaddr(ip)[0]
            except:
                pass
        target += ':' + port
        target = target.ljust(35)
        line = preamble + target + rest
    print(line)
