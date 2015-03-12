#!/usr/bin/python
#
# Converts an apacheConfig record from LDAP, as used by mod_vhost_ldap,
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
            "(&(objectClass=apacheConfig)" +
            "(|(apacheServerName=%s)" +
            "(apacheServerAlias=%s)))",
           [host, host]))
if len(r) != 0:
    user = pwd.getpwuid(int(r[0][1]['apacheSuexecUid'][0]))
    serveralias = ""
    if 'apacheServerAlias' in r[0][1]:
        serveralias = "ServerAlias "+" ".join(r[0][1]['apacheServerAlias'])
    print """# do not trailing-slash DocumentRoot

<VirtualHost *:80>
	ServerName %(servername)s
	%(serveralias)s
	DocumentRoot %(docroot)s
	Alias /~%(uname)s %(homedir)s/web_scripts
	SuExecUserGroup %(uname)s %(uname)s
	Include conf.d/vhosts-common.conf
</VirtualHost>

<IfModule ssl_module>
	<VirtualHost *:443>
		ServerName %(servername)s
		%(serveralias)s
		DocumentRoot %(docroot)s
		Alias /~%(uname)s %(homedir)s/web_scripts
		SuExecUserGroup %(uname)s %(uname)s
		Include conf.d/vhosts-common-ssl.conf
		SSLCertificateFile /etc/pki/tls/certs/%(hname)s.pem
		SSLCertificateKeyFile /etc/pki/tls/private/scripts-2048.key
	</VirtualHost>
	<VirtualHost *:444>
		ServerName %(servername)s
		%(serveralias)s
		DocumentRoot %(docroot)s
		Alias /~%(uname)s %(homedir)s/web_scripts
		SuExecUserGroup %(uname)s %(uname)s
		Include conf.d/vhosts-common-ssl.conf
		Include conf.d/vhosts-common-ssl-cert.conf
		SSLCertificateFile /etc/pki/tls/certs/%(hname)s.pem
		SSLCertificateKeyFile /etc/pki/tls/private/scripts-2048.key
	</VirtualHost>
</IfModule>""" % {
    'servername': r[0][1]['apacheServerName'][0],
    'serveralias': serveralias,
    'docroot': r[0][1]['apacheDocumentRoot'][0],
    'uname': user[0],
    'homedir': user[5],
    'hname': host
}

# vim: set ts=4 sw=4 et:
