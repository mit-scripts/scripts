#!/bin/sh
cd settings || exit 1
vhosts=
check () {
    host -t A "$1" | grep -q " has address 18\.181\.0\.46$" && \
	vhosts=$vhosts\ $1
}
for i in *; do
    check "$i" || echo "warning: $i does not point to scripts!"
    check "www.$i"
    if echo "$i" | grep -q '\.mit\.edu$'; then
	check "$(echo "$i" | sed 's/\.mit\.edu$//')"
    fi
done
echo "ServerName vhosts.mit.edu"
echo "ServerAlias$vhosts"
