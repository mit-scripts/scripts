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

FEDORA		= fc$(shell lsb_release -rs)
upstream_yum	= httpd openssh autofs
gems		= pony:1.8 fcgi:0.9.2.1
upstream_gems	= rubygem-pony rubygem-fcgi
upstream_eggs   = python-authkit
upstream	= openafs hesiod $(upstream_yum) $(upstream_gems) $(upstream_eggs) moira zephyr zephyr.i686 python-zephyr python-afs python-moira python-hesiod athena-aclocal discuss fuse-python
oursrc		= execsys tokensys accountadm httpdmods logview nss_nonlocal nss_nonlocal.i686 athrun php_scripts scripts-wizard scripts-base scripts-static-cat fuse-better-mousetrapfs scripts-munin-plugins scripts-krb5-localauth shackle
allsrc		= $(upstream) $(oursrc)
oursrcdir	= ${PWD}/../common/oursrc
patches		= ${PWD}/../common/patches
specs		= ${PWD}/specs

topdir		= ${HOME}/rpmbuild
tmp_build	= $(topdir)/BUILD
rpm_specs	= $(topdir)/SPECS
tmp_specs	= $(topdir)/SPECS-SCRIPTS
tmp_src		= $(topdir)/SOURCES
out_rpms	= $(topdir)/RPMS
out_srpms	= $(topdir)/SRPMS
out_sbin	= $(topdir)/sbin

dload		= ${PWD}/.dload
openafs_url	= "http://www.openafs.org/dl/openafs/1.8.4/openafs-1.8.4-1.src.rpm"
#zephyr_url	= "http://zephyr.1ts.org/files/zephyr-3.0.2.tar.gz"

PKG		= $(patsubst %.i686,%,$@)
scriptsversion	= $(shell git describe --dirty --match root | awk -F- '{print $$2 + 419 "." $$3 ($$4 ? "." $$4 : "")}')

.PHONY: minimal-clean

info:
	@echo "The following packages are available:"
	@echo "$(allsrc)"
	@echo "Run 'make all' to build all packages."

minimal-clean:
	rm -rf $(topdir) $(dload)

clean: minimal-clean
	rm -rf $(out_rpms) $(out_srpms) $(out_sbin)
	rm -f download_stamp

mkdir-tree:
	rpmdev-setuptree
	mkdir -p $(out_sbin)
	mkdir -p $(tmp_specs)
	ln -sTf $(topdir) rpmbuild

openafs openafs-kernel ${tmp_specs}/openafs.spec: $(dload)/$(notdir $openafs_url)
$(dload)/$(notdir $openafs_url):
	wget -P $(dload) $(openafs_url)

download: download_stamp
download_stamp:
	mkdir -p $(dload)
	cd $(dload) && yumdownloader --disablerepo=scripts --source $(upstream_yum)
	#wget -P $(dload) $(zephyr_url)
	cd $(tmp_src) && wget -nd -r -l1 -np -A.orig.tar.gz https://debathena.mit.edu/apt/pool/debathena/d/debathena-moira/
	$(foreach gem, $(gems), cd $(tmp_src) && gem fetch $(firstword $(subst :, ,$(gem))) -v $(lastword $(subst :, ,$(gem)));)
	spectool -g -R $(specs)/hesiod.spec
	spectool -g -R $(specs)/zephyr.spec
	spectool -g -R $(specs)/python-zephyr.spec
	spectool -g -R $(specs)/python-afs.spec
	spectool -g -R $(specs)/python-moira.spec
	spectool -g -R $(specs)/python-hesiod.spec
	spectool -g -R $(specs)/python-authkit.spec
	spectool -g -R $(specs)/fuse-python.spec
	touch download_stamp

	cd $(tmp_src) && wget -nd -r -l1 -np -A.tar.gz https://debathena.mit.edu/apt/pool/debathena/d/debathena-aclocal/
	cd $(tmp_src) && wget -nd -r -l1 -np -A.orig.tar.gz https://debathena.mit.edu/apt/pool/debathena/d/debathena-discuss/
	cp $(oursrcdir)/discuss/* $(tmp_src)

copy-patches: mkdir-tree
	cp $(patches)/*.patch $(tmp_src)

install-srpms: mkdir-tree download
	rpm $(rpm_args) -i $(dload)/*.src.rpm 2>/dev/null

# If we have a spec, just copy it.
${tmp_specs}/%.spec: ${specs}/%.spec mkdir-tree
	cp $< $@

# If we have a spec patch, install the SRPM and then patch it.
${tmp_specs}/%.spec: ${specs}/%.spec.patch install-srpms
	@set -ex; \
	rm -f $@.orig; \
	rm -f $@.specs.~*~; \
	patch -bV numbered -o $@ ${rpm_specs}/$*.spec $<

# 1. use the package's Makefile to delete leftover files and run autoconf
# 2. create a tarball (we want it to contain the autoconf output)
$(tmp_src)/%.tar.gz: $(oursrcdir)/% $(oursrcdir)/%/* mkdir-tree
	@set -ex; \
	cd ${oursrcdir}; \
	pushd $<; \
	if [ -x ./mrproper ]; then \
		./mrproper; \
		if [ -e configure.in ] || [ -e configure.ac ]; then \
			autoconf; \
		fi; \
	fi; \
	popd; \
	tar -czf $@ $*;

# Build a tarball for each package, if we can.
oursrcdirs := $(notdir $(wildcard $(oursrcdir)/*))
${oursrcdirs}: %: $(tmp_src)/%.tar.gz
${oursrcdirs:%=%.i686}: %.i686: $(tmp_src)/%.tar.gz

#setup: install-srpms copy-patches copy-specs patch-specs tarballs
setup: copy-patches

oursrc:
	make $(oursrc)

upstream: mkdir-tree download
	make $(upstream)

all:
	make $(allsrc)

$(oursrc): rpmbuild_args += --define 'scriptsversion $(scriptsversion)'

mock_chroot = scripts-${FEDORA}-`uname -m`
mock_args = -r ${mock_chroot} ${rpmbuild_args}

%.i686: mock_chroot = scripts-${FEDORA}-i686
%.i686: mock_args += --arch=i686 --define="_lib lib"

define build-rpm =
rpmbuild ${rpmbuild_args} -bs $<
/usr/bin/mock ${mock_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`
endef

%: ${tmp_specs}/%.spec setup
	$(build-rpm)
%.i686: ${tmp_specs}/%.spec setup
	$(build-rpm)

$(upstream) openafs-kernel: rpmbuild_args += --define 'scriptsversion $(scriptsversion)'

openafs-kernel: ${tmp_specs}/openafs.spec setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs $<
	/usr/bin/mock -r scripts-${FEDORA}-`uname -m` --clean
	/usr/bin/mock -r scripts-${FEDORA}-`uname -m` --install elfutils-libelf-devel
	/usr/bin/mock -r scripts-${FEDORA}-`uname -m` --no-clean ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/openafs*.src.rpm | head -1`

#sort -n sorts "2.6.25-1" later than "2.6.25.1-1", so it's Wrong
#kernvers = $(shell rpm -q --qf "%{Version}-%{Release}\n" --whatprovides kernel | sort -n | tail -n1)
kernvers = $(shell uname -r | sed "s/\(.*\)[.].*/\1/")
kvariants = ''
openafs_rpmbuild_args = --define "fedorakmod 1" --define "kvariants $(kvariants)" --define "kernvers $(kernvers)"
openafs: rpmbuild_args += $(openafs_rpmbuild_args) --define "build_userspace 1" --define "build_modules 0"
openafs-kernel: rpmbuild_args += $(openafs_rpmbuild_args) --define "build_userspace 0" --define "build_modules 1"

frob-openafs:
	@set -ex; \
	if [ ! -d "/etc/openafs/" ]; then \
	echo "/etc/openafs does not exist"; \
	exit 1; \
	else \
	ln -nfs /etc/openafs/* /usr/vice/etc/; \
	fi

fedora:
	make upstream
	rpm -ivh $(out_rpms)/`uname -m`/openafs-devel*.rpm
	make oursrc
