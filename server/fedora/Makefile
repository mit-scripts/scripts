# Makefile for building scripts.mit.edu Fedora packages
# Copyright (C) 2006  Jeff Arnold <jbarnold@mit.edu>
#                and  Joe Presbrey <presbrey@mit.edu>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
# See /COPYRIGHT in this repository for more information.

upstream_yum	= krb5 krb5.i586 httpd openssh
upstream	= openafs $(upstream_yum) moira cluster-glue heartbeat pacemaker
oursrc		= execsys tokensys accountadm httpdmods logview sql-signup nss_nonlocal nss_nonlocal.i586 whoisd mit-zephyr athrun php_scripts scripts-base
allsrc		= $(upstream) $(oursrc)
oursrcdir	= ${PWD}/../common/oursrc
patches		= ${PWD}/../common/patches
specs		= ${PWD}/specs

topdir		= ${HOME}/rpmbuild
tmp_build	= $(topdir)/BUILD
tmp_specs	= $(topdir)/SPECS
tmp_src		= $(topdir)/SOURCES
out_rpms	= $(topdir)/RPMS
out_srpms	= $(topdir)/SRPMS
out_sbin	= $(topdir)/sbin

dload		= ${PWD}/.dload
server_url	= "http://web.mit.edu/scripts/src"
server_arch	= "fedora.stable"
openafs_url	= "http://dl.openafs.org/dl/openafs/1.4.11/openafs-1.4.11-1.1.1.src.rpm"
clusterglue_url	= "http://kojipkgs.fedoraproject.org/packages/cluster-glue/1.0/0.11.b79635605337.hg.fc12/src/cluster-glue-1.0-0.11.b79635605337.hg.fc12.src.rpm"
heartbeat_url	= "http://kojipkgs.fedoraproject.org/packages/heartbeat/3.0.0/0.5.0daab7da36a8.hg.fc12/src/heartbeat-3.0.0-0.5.0daab7da36a8.hg.fc12.src.rpm"
pacemaker_url	= "http://kojipkgs.fedoraproject.org/packages/pacemaker/1.0.5/5.fc12/src/pacemaker-1.0.5-5.fc12.src.rpm"

PKG		= $(patsubst %.i586,%,$@)

.PHONY: minimal-clean

info:
	@echo "The following packages are available:"; \
	echo "$(allsrc)"; \
	echo "Run 'make all' to build all packages."

minimal-clean:
	rm -rf $(topdir) $(dload)

clean: minimal-clean
	rm -rf $(out_rpms) $(out_srpms) $(out_sbin)

mkdir-tree:
	@rpmdev-setuptree
	mkdir -p $(out_sbin)
	ln -sTf $(topdir) rpmbuild

download: download_stamp
download_stamp: | SRPMS/mit-zephyr-2.1-6.src.rpm
	@mkdir -p $(dload); \
	#wget -qO- -nv $(server_url)/$(server_arch) | xargs make
	cd $(dload) && yumdownloader --disablerepo=scripts --source $(upstream_yum)
	wget -P $(dload) $(openafs_url)
	wget -P $(dload) $(clusterglue_url)
	wget -P $(dload) $(heartbeat_url)
	wget -P $(dload) $(pacemaker_url)
	cd $(tmp_src) && wget -nd -r -l1 -np -A.orig.tar.gz http://debathena.mit.edu/apt/pool/debathena/d/debathena-moira/
	touch download_stamp

%.src.rpm:
	wget -q -nv -N -B $(server_url) -nd -nH -P $(dload) $(server_url)/$*.src.rpm

copy-patches: mkdir-tree
	@cp $(patches)/*.patch $(tmp_src); \
	cd $(tmp_src);

install-srpms: mkdir-tree download
	rpm $(rpm_args) -i $(dload)/*.src.rpm 2>/dev/null;

copy-specs: mkdir-tree
	cp ${specs}/*.spec $(tmp_specs)

patch-specs: install-srpms
	@cd ${tmp_specs}; \
	list=`ls ${specs}/*.spec.patch`; \
	for i in $$list; do \
		patch < $$i; \
	done; \
	list2=`svn ls ${oursrcdir}`; \
	for i in $$list2; do \
		base=`basename $$i`; \
		version=`svnversion ${oursrcdir}/$$i`; \
		version=$${version//:/_}; \
		echo "$$i version $$version"; \
		sed --in-place \
			-e "s/SVNVERSION_TO_UPDATE/$${version}/" \
		${tmp_specs}/$$base.spec; \
	done;

# 1. use the package's Makefile to delete leftover files and run autoconf
# 2. create a tarball (we want it to contain the autoconf output)
tarballs: mkdir-tree
	@cd ${oursrcdir}; \
	list=`find -mindepth 1 -maxdepth 1 -type d | grep -v ".svn"`; \
	for i in $$list; do \
		pushd $$i; \
		if [ -x ./mrproper ]; then \
			./mrproper; \
			autoconf; \
		fi; \
		popd; \
		tar -czf $(tmp_src)/$$i.tar.gz $$i; \
	done;

#setup: install-srpms copy-patches copy-specs patch-specs tarballs
setup: copy-patches copy-specs patch-specs tarballs

oursrc:
	make $(oursrc)

upstream: mkdir-tree download
	make $(upstream)

all:
	make $(allsrc)

$(oursrc): rpmbuild_args += --define 'scriptsversion $(shell svnversion ${oursrcdir}/$** | tr ':' '_')'

$(filter %.i586,$(oursrc)): %.i586: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc11-i386 --arch=i586 ${rpmbuild_args} --define="_lib lib" -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

$(filter-out %.i586,$(oursrc)): %: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc11-`uname -m` ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

$(upstream) openafs-kernel: rpmbuild_args += --define 'scriptsversion $(shell svnversion ${patches} | tr ':' '_')'

$(filter %.i586,$(upstream)): %.i586: setup patch-specs
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc11-i386 --arch=i586 ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

$(filter-out %.i586,$(upstream)): %: setup patch-specs
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc11-`uname -m` ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

openafs-kernel: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/openafs*.spec
	/usr/bin/mock -r scripts-fc11-`uname -m` ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/openafs*.src.rpm | head -1`

#sort -n sorts "2.6.25-1" later than "2.6.25.1-1", so it's Wrong
#kernvers = $(shell rpm -q --qf "%{Version}-%{Release}\n" --whatprovides kernel | sort -n | tail -n1)
kernvers = $(shell uname -r | sed "s/\(.*\)[.].*/\1/")
kvariants = ''
openafs_rpmbuild_args = --define "fedorakmod 1" --define "kvariants $(kvariants)" --define "kernvers $(kernvers)"
openafs: rpmbuild_args += $(openafs_rpmbuild_args)
openafs-kernel: rpmbuild_args += $(openafs_rpmbuild_args) --define "build_userspace 0" --define "build_modules 1"

suexec: #install-srpms
	@rm -rf ${tmp_src}/httpd-2*/; \
	tar zxvf ${tmp_src}/httpd-2*.tar.gz; \
	cd httpd-2*; \
	patch -p1 < ${patches}/httpd-suexec-scripts.patch; \
	autoreconf; \
	./configure --prefix=/etc/httpd --with-suexec-userdir=web_scripts --with-suexec-caller=apache --with-suexec-uidmin=50 --with-suexec-gidmin=50 --with-suexec-docroot=/ --with-suexec-trusteddir=/usr/libexec/scripts-trusted; \
	pushd support; \
	mkdir -p ${out_sbin}; make suexec && cp suexec ${out_sbin}; \
	popd; \
	rm -rf httpd-2*; \
	echo; \
	echo "suexec binary written to ${out_sbin}."; \
	echo "Run 'make install-suexec' as root to install it.";

install-suexec:
	install -m 4510 -o 0 -g apache ${out_sbin}/suexec /usr/sbin/;

frob-openafs:
	@if [ ! -d "/etc/openafs/" ]; then \
	echo "/etc/openafs does not exist"; \
	exit 1; \
	else \
	ln -nfs /etc/openafs/* /usr/vice/etc/; \
	fi

# The following packages are needed for our packages
basic-deps	= kernel-devel rpm-build rpmdevtools mock gcc autoconf patch krb5-workstation glibc-devel.i586 glibc-devel libtool libgcc.i586
oursrc-deps	= hesinfo openldap-clients openldap-devel.i586 php-devel
httpdmods-deps	= httpd-devel
httpd-deps	= xmlto db4-devel expat-devel zlib-devel libselinux-devel apr-devel apr-util-devel pcre-devel openssl-devel distcache-devel
krb5-deps	= bison ncurses-devel texinfo keyutils-libs-devel texinfo-tex texlive-latex
openafs-deps	= pam-devel automake
mit-zephyr-deps	= readline-devel hesiod-devel hesiod-devel.i586 hesiod.i586 libXt.i586 #compat-readline43
openssh-deps	= gtk2-devel libX11-devel autoconf automake openssl-devel perl zlib-devel audit-libs-devel util-linux groff man pam-devel tcp_wrappers-devel krb5-devel libselinux-devel audit-libs xauth pango-devel cairo-devel libedit-devel nss-devel fipscheck-devel
php-deps	= bzip2-devel curl-devel gmp-devel libstdc++-devel sqlite-devel gcc-c++ libc-client-devel mysql-devel postgresql-devel unixODBC-devel libxml2-devel net-snmp-devel libxslt-devel libxml2-devel libXpm-devel libjpeg-devel t1lib-devel libmcrypt-devel mhash-devel libtidy-devel freetds-devel aspell-devel recode-devel
install-deps:
	yum -y install $(basic-deps) $(oursrc-deps) $(httpdmods-deps) $(httpd-deps) $(krb5-deps) $(openafs-deps) $(mit-zephyr-deps) $(openssh-deps) $(php-deps)
	rpm -ivh http://kojipkgs.fedoraproject.org/packages/compat-readline43/4.3/3/i386/compat-readline43-4.3-3.i386.rpm
#	rpm -ivh http://download.fedora.redhat.com/pub/fedora/linux/core/6/i386/os/Fedora/RPMS/compat-readline43-4.3-3.i386.rpm

fedora:
	make install-deps
	make upstream
	rpm -ivh $(out_rpms)/`uname -m`/openafs-devel*.rpm
	make oursrc
