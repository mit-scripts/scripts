#!/bin/sh

# Run this as root on scripts.

/usr/bin/ldapsearch -LLL -z 0 -b ou=People,dc=scripts,dc=mit,dc=edu -s one -x -D 'cn=Directory Manager' -y /etc/signup-ldap-pw '' cn homeDirectory | \
	perl -0pe 's/\n //g; s/^dn: .*\ncn: (.*)\nhomeDirectory: (.*)\n\n/$1 $2\n/gm'
