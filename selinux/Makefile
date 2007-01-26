include /usr/share/selinux/devel/Makefile
#include /usr/share/selinux/devel/include/Makefile

/usr/share/selinux/devel/include/Makefile:
	yum -y install selinux-policy-devel

build/%.fc: %.fc
	rm -rf tmp

install:
	/usr/sbin/semodule -n -i openafs.pp;
	/usr/sbin/semodule -n -i scripts.pp;
	/usr/sbin/semodule -n -i signup.pp;
	/usr/sbin/semodule -n -i admof.pp;
	/usr/sbin/semodule -n -i nagios-nrpe.pp;
	/usr/sbin/semodule -n -i zephyr.pp;
	/usr/sbin/semodule -R
	/usr/sbin/getenforce
