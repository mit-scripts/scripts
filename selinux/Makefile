include /usr/share/selinux/devel/Makefile
#include /usr/share/selinux/devel/include/Makefile

/usr/share/selinux/devel/include/Makefile:
	yum -y install selinux-policy-devel

build/%.fc: %.fc
	rm -rf tmp

install:
	/usr/sbin/semodule -i admof.pp;
	/usr/sbin/semodule -i nagios-nrpe.pp;
	/usr/sbin/semodule -i openafs.pp;
	/usr/sbin/semodule -i scripts.pp;
	/usr/sbin/semodule -i signup.pp;
	/usr/sbin/semodule -i zephyr.pp;
	/usr/sbin/getenforce
