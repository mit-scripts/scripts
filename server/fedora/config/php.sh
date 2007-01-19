#!/bin/bash

mkdir -p /etc/php.d/disable
mv -f /etc/php.d/*.ini -u /etc/php.d/disable/
rm -f /etc/php.d/*.ini
pushd /etc/php.d/ >/dev/null
touch `ls /etc/php.d/disable/*.ini | cut -d/ -f5` -t01010000
popd >/dev/null

svn revert /etc/php.d/scripts.ini

restorecon -R /etc
