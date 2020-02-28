#!/usr/bin/python

import sys
import subprocess
import re
import socket
from gnlpy import ipvs

# Ignore the HTTP request
while sys.stdin.readline().strip():
    pass

print("HTTP/1.0 200 OK\r")
print("Content-type: text/html\r")
print("\r")
print("<html><head><title>scripts.mit.edu server status</title></head><body><h1>scripts.mit.edu server status</h1><p>The following table shows a list of the servers that are currently handling web requests for scripts.mit.edu:</p>")

def row(target, weight, inactive, active):
    try:
        target = socket.gethostbyaddr(target)[0]
    except:
        pass
    line = '<tr><td>' + target + '</td><td>' + str(weight) + '</td><td>'
    line += str(inactive) + '</td><td>' + str(active) + '</td></tr>'
    return line

pools = ipvs.IpvsClient().get_pools()
for pool in pools:
    mark = pool.service().fwmark()
    if mark == 22:
        pool_name = 'Fedora 20'
    elif mark == 32:
        pool_name = 'Fedora 30'
    # TODO: Add query parameter/URL for all pools?
    else:
        continue
    print("<table><tr style='text-align: left'><th>%s servers</th><th>Weight</th><th>ActiveConn</th><th>InActConn</th></tr>" % (pool_name,))
    for dest in pool.dests():
        print(row(dest.ip(), dest.weight(), dest.counters().get('active_conns', 0), dest.counters().get('inact_conns', 0)))
    print("</table>")
print("</body></html>")
