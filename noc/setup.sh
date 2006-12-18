#!/bin/sh

chmod 711 /home/noc/
chown -R nagios:nagios /home/noc/

find /home/noc/ -type f | xargs chmod 644
find /home/noc/ -type d | xargs chmod 755
find /home/noc/ -name '*.cgi' -or -name '*.php' -or -name '*.pl' -or -name '*.sh' | xargs chmod a+x

chown -R nagios:apache /home/noc/html/ /home/noc/ng/html/ /home/noc/ng/log/ /home/noc/ng/rrd/
chmod -R g-w /home/noc/html/* /home/noc/ng/html/*
chmod -R g+w /home/noc/ng/log/ /home/noc/ng/rrd/
chmod g+w /home/noc/ng/log/ /home/noc/ng/rrd/
