#!/bin/sh

chown -R nagios:nagios /home/noc/
chmod 711 /home/noc/

find /home/noc/ -type f | xargs -n1 chmod 644
find /home/noc/ -type d | xargs -n1 chmod 755
find /home/noc/ -name '*.cgi' -or -name '*.php' -or -name '*.pl' -or -name '*.sh' | xargs -n1 chmod a+x

chown -R nagios:apache /home/noc/html/ /home/noc/ng/html/ /home/noc/ng/log/ /home/noc/ng/rrd/
chmod -R g-w /home/noc/html/* /home/noc/ng/html/*
chmod -R g+w /home/noc/ng/log/ /home/noc/ng/rrd/
chmod g+w /home/noc/ng/log/ /home/noc/ng/rrd/

if [ ! -h /etc/nagios ]; then
	mv /etc/nagios /etc/nagios_OLD
	ln -nfs /home/noc/nagios/ /etc/nagios
fi

chown -R root:root /home/noc/nagios/
find /home/noc/nagios/ -type f | xargs -n1 chmod 644
find /home/noc/nagios/ -type d | xargs -n1 chmod 755

chown -R root:nagios /home/noc/nagios/private/
chmod -R o-rwx /home/noc/nagios/private/
