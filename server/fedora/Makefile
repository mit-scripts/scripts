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

upstream_yum	= krb5 httpd openssh pysvn php
upstream	= openafs $(upstream_yum)
oursrc		= execsys tokensys accountadm httpdmods logview sql-signup nss_nonlocal nss_nonlocal.i386 whoisd mit-zephyr nss-ldapd nss-ldapd.i386 athrun php_scripts scripts-base
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
openafs_url	= "http://dl.openafs.org/dl/openafs/1.4.10/openafs-1.4.10-1.1.1.src.rpm"
nss_ldapd_url	= "http://download.opensuse.org/repositories/network:/ldap/openSUSE_Factory/src/nss-ldapd-0.6.8-2.1.src.rpm"

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
	cd $(dload) && yumdownloader --source $(upstream_yum)
	wget -P $(dload) $(nss_ldapd_url)
	wget -P $(dload) $(openafs_url)
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

$(filter %.i386,$(oursrc)): %.i386: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	setarch i386 rpmbuild $(rpmbuild_args) --target=i386 --define="_lib lib" -bb ${tmp_specs}/$**.spec

$(filter-out %.i386,$(oursrc)): %: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild $(rpmbuild_args) -bb ${tmp_specs}/$**.spec

$(upstream) openafs-kernel: rpmbuild_args += --define 'scriptsversion $(shell svnversion ${patches} | tr ':' '_')'

$(upstream): setup patch-specs
	rpmbuild $(rpmbuild_args) -ba ${tmp_specs}/$@.spec

openafs-kernel: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild $(rpmbuild_args) -bb ${tmp_specs}/openafs*.spec

#sort -n sorts "2.6.25-1" later than "2.6.25.1-1", so it's Wrong
#kernvers = $(shell rpm -q --qf "%{Version}-%{Release}\n" --whatprovides kernel | sort -n | tail -n1)
kernvers = $(shell uname -r | sed "s/\(.*\)[.].*/\1/")
kvariants = ''
openafs_rpmbuild_args = --define "fedorakmod 1" --define "kvariants $(kvariants)" --define "kernvers $(kernvers)" --nodeps
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
basic-deps	= kernel-devel rpm-build rpmdevtools gcc autoconf patch krb5-workstation glibc-devel.i386 glibc-devel libtool libgcc.i386
oursrc-deps	= hesinfo openldap-clients php-devel
httpdmods-deps	= httpd-devel
httpd-deps	= xmlto db4-devel expat-devel zlib-devel libselinux-devel apr-devel apr-util-devel pcre-devel openssl-devel distcache-devel
krb5-deps	= bison ncurses-devel texinfo keyutils-libs-devel texinfo-tex
openafs-deps	= pam-devel automake
mit-zephyr-deps	= readline-devel hesiod-devel hesiod-devel.i386 hesiod.i386 libXt.i386 #compat-readline43
openssh-deps	= gtk2-devel libX11-devel autoconf automake openssl-devel perl zlib-devel audit-libs-devel util-linux groff man pam-devel tcp_wrappers-devel krb5-devel libselinux-devel audit-libs xauth gobject-devel pango-devel cairo-devel libedit-devel nss-devel
install-deps:
	yum -y install $(basic-deps) $(oursrc-deps) $(httpdmods-deps) $(httpd-deps) $(krb5-deps) $(openafs-deps) $(mit-zephyr-deps) $(openssh-deps)
	rpm -ivh ftp://ftp.muug.mb.ca/mirror/fedora/linux/core/6/i386/os/Fedora/RPMS/compat-readline43-4.3-3.i386.rpm
#	rpm -ivh http://download.fedora.redhat.com/pub/fedora/linux/core/6/i386/os/Fedora/RPMS/compat-readline43-4.3-3.i386.rpm

fedora:
	make install-deps
	make upstream
	rpm -ivh $(out_rpms)/`uname -m`/openafs-devel*.rpm
	make oursrc
