#!/usr/bin/python
#
# Converts an scriptsVhost record from LDAP, as used by mod_vhost_ldap,
# into a <VirtualHost> record as used in an Apache conf.d directory.
# Useful for adding things like SSL server certs that mod_vhost_ldap
# doesn't support.
#
# Usage:
# scripts# cd /etc/httpd/vhosts.d
# scripts# ./reify-vhost.py geofft > geofft.conf
# scripts# service httpd graceful
# 
# Geoffrey Thomas <geofft@mit.edu>, 2008, public domain.

import ldap
import ldap.filter
import pwd
import sys

ll = ldap.initialize("ldapi://%2fvar%2frun%2fslapd-scripts.socket/")
ll.simple_bind_s("", "")

host = sys.argv[1]

r = ll.search_s(
    "ou=VirtualHosts,dc=scripts,dc=mit,dc=edu",
    ldap.SCOPE_SUBTREE,
    ldap.filter.filter_format(
            "(&(objectClass=scriptsVhost)" +
            "(|(scriptsVhostName=%s)" +
            "(scriptsVhostAlias=%s)))",
           [host, host]))
if len(r) != 0:
    serveralias = ""
    if 'scriptsVhostAlias' in r[0][1]:
        serveralias = "ServerAlias "+" ".join(r[0][1]['scriptsVhostAlias'])
    print """\
<IfModule ssl_module>
	<VirtualHost *:443>
		ServerName %(servername)s
		%(serveralias)s
		Include conf.d/vhost_ldap.conf
		Include conf.d/vhosts-common-ssl.conf
		SSLCertificateFile /etc/pki/tls/certs/%(hname)s.pem
		SSLCertificateKeyFile /etc/pki/tls/private/scripts-2048.key
	</VirtualHost>
	<VirtualHost *:444>
		ServerName %(servername)s
		%(serveralias)s
		Include conf.d/vhost_ldap.conf
		Include conf.d/vhosts-common-ssl.conf
		Include conf.d/vhosts-common-ssl-cert.conf
		SSLCertificateFile /etc/pki/tls/certs/%(hname)s.pem
		SSLCertificateKeyFile /etc/pki/tls/private/scripts-2048.key
	</VirtualHost>
</IfModule>""" % {
    'servername': r[0][1]['scriptsVhostName'][0],
    'serveralias': serveralias,
    'hname': host
}

# vim: set ts=4 sw=4 et:
