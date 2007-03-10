#!/bin/bash

S_ON='acpid auditd autofs crond execsys-binfmt httpd ip6tables iptables lm_sensors mcstrans mdmonitor named network nrpe openafs-client restorecond sshd syslog sysstat zhm ntpd netfs nfslock portmap nfs'
S_OFF='NetworkManager NetworkManagerDispatcher anacron atd avahi-dnsconfd capi cpuspeed cups dc_client dc_server dhcdbd diskdump firstboot gpm haldaemon irda isdn kudzu mdmpd messagebus multipathd netdump netplugd nscd pcscd psacct rdisc readahead_later rpcgssd rpcidmapd rpcsvcgssd saslauthd sendmail snmpd snmptrapd spamassassin wpa_supplicant ypbind avahi-daemon readahead_early xfs xinetd yum-updatesd irqbalance smartd postfix'

for s in $S_OFF; do
	/sbin/chkconfig $s off
	/sbin/service $s stop
done

for s in $S_ON; do
	/sbin/chkconfig --add $s
	/sbin/chkconfig $s on
	#/sbin/service $s status || runcon system_u:system_r:initrc_t:s0 /sbin/service $s start
done

restorecon -R /etc
