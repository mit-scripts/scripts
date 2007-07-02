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

upstream	= openafs krb5 httpd mit-zephyr
oursrc		= execsys tokensys accountadm httpdmods logview sql-signup
allsrc		= $(upstream) $(oursrc)
oursrcdir	= ${PWD}/../common/oursrc
patches		= ${PWD}/../common/patches
metapatches	= ${PWD}/meta-patches
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

openafs_rpm_args = -E "%define kernvers $(shell rpm -q --qf "%{Version}-%{Release}\n" --whatprovides kernel | sort -n | tail -n1)"

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
	@rpmdev-setuptree; \
	mkdir -p $(out_sbin); \
	ln -s $(topdir) rpmbuild;

download:
	-@wget -O- -nv $(server_url)/$(server_arch) | wget -i- -nv -N -B $(server_url)/ -nd -nH -P $(dload);

copy-patches: mkdir-tree
	@cp $(patches)/*.patch $(tmp_src); \
	cd $(tmp_src); \
	list=`ls $(metapatches)/*.patch`; \
        for i in $$list; do \
                patch < $$i; \
        done;

install-srpms: mkdir-tree download
	rpm $(rpm_args) -i $(dload)/*.src.rpm 2>/dev/null;

copy-specs: mkdir-tree
	cp ${specs}/*.spec $(tmp_specs)

patch-specs: install-srpms
	@cd ${tmp_specs}; \
	list=`ls ${specs}/*.spec.patch`; \
	for i in $$list; do \
		patch < $$i; \
	done;

# 1. use the package's Makefile to delete leftover files and run autoconf
# 2. create a tarball (we want it to contain the autoconf output)
create-tarballs: mkdir-tree
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

setup: install-srpms copy-patches copy-specs patch-specs create-tarballs

# Do not work:
#rpms: setup
#	rpmbuild $(rpm_args) -bb ${tmp_specs}/$(allsrc);
#
#srpms: setup
#	rpmbuild $(rpm_args) -bs ${tmp_specs}/$(allsrc);

oursrc:
	make $(oursrc)

upstream:
	make $(upstream)

all:
	make $(allsrc)

$(allsrc): setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild -ba ${tmp_specs}/$@*.spec

openafs-kernel: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild $(openafs_rpm_args) -bb --define "build_userspace 0" --define "build_modules 1" ${tmp_specs}/openafs*.spec

suexec: install-srpms
	@rm -rf ${tmp_src}/httpd-2*/; \
	tar zxvf ${tmp_src}/httpd-2*.tar.gz; \
	cd httpd-2*; \
	patch -p1 < ${patches}/httpd-suexec-scripts.patch; \
	./configure --prefix=/etc/httpd --with-suexec-userdir=web_scripts --with-suexec-caller=apache --with-suexec-uidmin=50 --with-suexec-gidmin=50 --with-suexec-docroot=/; \
	pushd support; \
	mkdir -p ${out_sbin}; make suexec && cp suexec ${out_sbin}; \
	popd; \
	rm -rf httpd-2*; \
	echo; \
	echo "suexec binary written to ${out_sbin}."; \
	echo "Run 'make install-suexec' as root to install it.";

install-suexec:
	install -m 4510 -o 0 -g apache ${PWD}/sbin/suexec /usr/sbin/;

frob-openafs:
	@if [ ! -d "/etc/openafs/" ]; then \
	echo "/etc/openafs does not exist"; \
	exit 1; \
	else \
	ln -nfs /etc/openafs/* /usr/vice/etc/; \
	fi

# The following packages are needed for our packages
# basic deps: kernel-devel through krb5-workstation
# oursrc: hesinfo
# httpdmods: httpd-devel
# httpd: xmlto through distcache-devel
# krb5: bison through texinfo keyutils-libs-devel
# openafs: pam-devel through automake
# mit-zephyr: readline-devel hesiod.i386 libXt.i386 compat-readline43
install-deps:
	yum -y install kernel-devel rpm-build rpmdevtools gcc autoconf patch krb5-workstation hesinfo httpd-devel xmlto db4-devel expat-devel zlib-devel libselinux-devel apr-devel apr-util-devel pcre-devel openssl-devel distcache-devel bison ncurses-devel texinfo keyutils-libs-devel pam-devel automake readline-devel hesiod.i386 libXt.i386
	rpm -ivh http://download.fedora.redhat.com/pub/fedora/linux/core/6/i386/os/Fedora/RPMS/compat-readline43-4.3-3.i386.rpm
