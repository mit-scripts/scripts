#!/bin/sh
cd /mit/scripts/vhosts/settings/ || exit 1
echo "ServerName vhosts.mit.edu"
echo -n "ServerAlias "; echo * | perl -pe 's/(\S+)\.mit\.edu/\1.mit.edu \1/g'
