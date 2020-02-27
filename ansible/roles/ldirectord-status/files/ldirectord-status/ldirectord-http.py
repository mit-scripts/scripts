#!/usr/bin/python

import sys
import subprocess
import re
import socket

# Ignore the input from the finger protocol
sys.stdin.readline()

print("HTTP/1.0 200 OK")
print("Content-type: text/html")
print("")
print("<html><head><title>scripts.mit.edu server status</title></head><body><h1>scripts.mit.edu server status</h1><p>The following table shows a list of the servers that are currently handling web requests for scripts.mit.edu:</p>")
lines = subprocess.check_output(['/sbin/ipvsadm', '-L', '-n']).split(b'\n')
realserver = re.compile('(  -> )([^:]*):([^ ]*) *[^ ]* *([^ ]*) *([^ ]*) *([^ ]*)')
fwm = re.compile('^FWM  ([0-9]*)')
ipaddress = re.compile('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
show = 1
header = ''
for line in lines:
    line = line.decode('utf8')
    fwmline = fwm.match(line)
    if fwmline:
        if show:
            print("</table>")
        mark = fwmline.group(1)
        show = 1
        if mark == '22':
            pool = 'Fedora 20'
        elif mark == '32':
            pool = 'Fedora 30'
        else:
            show = 0
        if show:
            print("<p><b>%s servers</b></p><table>" % (pool))
            print(header)
    elif show:
        realline = realserver.match(line)
        if not realline:
            continue
        (preamble, ip, port, weight, inactive, active) = realline.groups()
        target = ip
        if ipaddress.match(ip):
            try:
                target = socket.gethostbyaddr(ip)[0]
            except:
                pass
        line = '<tr><td>' + target + '</td><td>' + weight + '</td><td>'
        line += inactive + '</td><td>' + active + '</td></tr>'
        if not header: # The header isn't set yet - this is it!
            header = line
            show = 0
        else:
            print(line)
if show:
    print("</table>")
print("</body></html>")
