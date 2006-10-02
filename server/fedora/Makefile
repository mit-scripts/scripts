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

upstream	= openafs krb5 httpd
oursrc		= execsys tokensys lockeradm sqladm
allsrc		= $(upstream) $(oursrc)
oursrcdir	= ${PWD}/../common/oursrc
patches		= ${PWD}/../common/patches
specs		= ${PWD}/specs

topdir		= ${PWD}/.tmp
tmp_build	= ${PWD}/.tmp/BUILD
tmp_specs	= ${PWD}/.tmp/SPECS
tmp_src		= ${PWD}/.tmp/SOURCES
out_rpms	= ${PWD}/RPMS
out_srpms	= ${PWD}/SRPMS
tree		= $(topdir) $(tmp_build) $(tmp_specs) $(tmp_src) $(out_rpms) $(out_srpms) 
out_sbin	= ${PWD}/sbin

dload		= ${PWD}/.dload
server_url	= "http://scripts.mit.edu/src"
server_arch	= "fedora.stable"

rpm_args	= -E '%define _smp_mflags -j4' -E '%define _topdir $(topdir)' -E '%define _rpmdir $(out_rpms)' -E '%define _srcrpmdir $(out_srpms)' -E '%define kernvers %(rpm -q --whatprovides kernel | sort | tail -1)'

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
	@mkdir -p $(tree);

download:
	-@wget -O- -nv $(server_url)/$(server_arch) | wget -i- -nv -nc -B $(server_url)/ -nd -nH -P $(dload);

copy-patches: mkdir-tree
	cp ${patches}/*.patch $(tmp_src)

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
	list=`find -mindepth 1 -maxdepth 1 -type d`; \
	for i in $$list; do \
		pushd $$i; \
		autoconf; \
		./configure; \
		make ready; \
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
	rpmbuild $(rpm_args) -ba ${tmp_specs}/$@*.spec

suexec: install-srpms
	@rm -rf ${tmp_src}/httpd-2*/; \
	tar zxvf ${tmp_src}/httpd-2*.tar.gz; \
	cd httpd-2*; \
	patch -p1 < ${patches}/httpd-suexec-scripts.patch; \
	./configure --prefix=/etc/httpd --with-suexec-userdir=web_scripts --with-suexec-caller=apache --with-suexec-uidmin=50 --with-suexec-gidmin=50 --with-suexec-docroot=/; \
	pushd support; \
	make suexec && mkdir ${out_sbin} && cp suexec ${out_sbin}; \
	popd; \
	rm -rf httpd-2*; \
	echo; \
	echo "suexec binary written to ${out_sbin}."; \
	echo "Run 'make install-suexec' as root to install it.";

install-suexec:
	install -m 4510 -o 0 -g apache ${PWD}/sbin/suexec /usr/sbin/;
