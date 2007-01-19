include /usr/share/selinux/devel/Makefile
#include /usr/share/selinux/devel/include/Makefile

/usr/share/selinux/devel/include/Makefile:
	yum -y install selinux-policy-devel

build/%.fc: %.fc
	rm -rf tmp

install:
	/usr/sbin/setenforce 0;
	/usr/sbin/semodule -i afsagent.pp;
	/usr/sbin/semodule -i afsd.pp;
	/usr/sbin/semodule -i misc.pp;
	/usr/sbin/getenforce
#	export SESTAT=`/usr/sbin/getenforce`;
#	/usr/sbin/setenforce $$SESTAT;
