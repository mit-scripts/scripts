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

upstream_yum	= krb5 krb5.i686 httpd openssh libgsasl
hackage		= cgi-3001.1.8.5 unix-handle-0.0.0
upstream_hackage = ghc-cgi ghc-unix-handle
gems		= pony:1.8 fcgi:0.9.2.1
upstream_gems	= rubygem-pony rubygem-fcgi
upstream_eggs   = python-authkit
upstream	= openafs $(upstream_yum) $(upstream_hackage) $(upstream_gems) $(upstream_eggs) moira zephyr zephyr.i686 python-zephyr python-afs python-moira python-hesiod athena-aclocal discuss
oursrc		= execsys tokensys accountadm httpdmods logview sql-signup nss_nonlocal nss_nonlocal.i686 whoisd athrun php_scripts scripts-wizard scripts-base scripts-static-cat fuse-better-mousetrapfs scripts-munin-plugins
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
openafs_url	= "https://www.openafs.org/dl/openafs/candidate/1.6.10pre1/openafs-1.6.10-0.pre1.src.rpm"
#zephyr_url	= "http://zephyr.1ts.org/files/zephyr-3.0.2.tar.gz"

PKG		= $(patsubst %.i686,%,$@)

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
	ln -sTf $(topdir) rpmbuild

download: download_stamp
download_stamp:
	mkdir -p $(dload)
	cd $(dload) && yumdownloader --disablerepo=scripts --source $(upstream_yum)
	wget -P $(dload) $(openafs_url)
	#wget -P $(dload) $(zephyr_url)
	cd $(tmp_src) && wget -nd -r -l1 -np -A.orig.tar.gz https://debathena.mit.edu/apt/pool/debathena/d/debathena-moira/
	cabal update
	cabal fetch --no-dependencies $(hackage)
	cp -a $(hackage:%=~/.cabal/packages/*/*/*/%.tar.gz) $(tmp_src)
	$(foreach gem, $(gems), gem fetch $(firstword $(subst :, ,$(gem))) -v $(lastword $(subst :, ,$(gem)));)
	spectool -g -R $(specs)/zephyr.spec
	spectool -g -R $(specs)/python-zephyr.spec
	spectool -g -R $(specs)/python-afs.spec
	spectool -g -R $(specs)/python-moira.spec
	spectool -g -R $(specs)/python-hesiod.spec
	spectool -g -R $(specs)/python-authkit.spec
	touch download_stamp

	cd $(tmp_src) && wget -nd -r -l1 -np -A.tar.gz https://debathena.mit.edu/apt/pool/debathena/d/debathena-aclocal/
	cd $(tmp_src) && wget -nd -r -l1 -np -A.orig.tar.gz https://debathena.mit.edu/apt/pool/debathena/d/debathena-discuss/
	cp $(oursrcdir)/discuss/* $(tmp_src)

copy-patches: mkdir-tree
	cp $(patches)/*.patch $(tmp_src)

install-srpms: mkdir-tree download
	rpm $(rpm_args) -i $(dload)/*.src.rpm 2>/dev/null

copy-specs: mkdir-tree
	cp ${specs}/*.spec $(tmp_specs)

# Remove old .orig files so we're not misled
patch-specs: install-srpms
	@set -ex; \
	cd ${tmp_specs}; \
	list=`ls ${specs}/*.spec.patch`; \
	rm -f *.orig; \
	rm -f *.spec.~*~; \
	for i in $$list; do \
		patch -bV numbered < $$i; \
	done; \
	list2=`svn ls ${oursrcdir}`; \
	for i in $$list2; do \
		base=`basename $$i`; \
		[ -e ${tmp_specs}/$$base.spec ] || continue; \
		version=`svnversion ${oursrcdir}/$$i`; \
		version=$${version//:/_}; \
		echo "$$i version $$version"; \
		sed --in-place \
			-e "s/SVNVERSION_TO_UPDATE/$${version}/" \
		${tmp_specs}/$$base.spec; \
	done

# 1. use the package's Makefile to delete leftover files and run autoconf
# 2. create a tarball (we want it to contain the autoconf output)
tarballs: mkdir-tree
	@set -ex; \
	cd ${oursrcdir}; \
	list=`find -mindepth 1 -maxdepth 1 -type d | grep -v ".svn"`; \
	for i in $$list; do \
		pushd $$i; \
		if [ -x ./mrproper ]; then \
			./mrproper; \
			if [ -e configure.in ] || [ -e configure.ac ]; then \
				autoconf; \
			fi; \
		fi; \
		popd; \
		tar -czf $(tmp_src)/$$i.tar.gz $$i; \
	done

#setup: install-srpms copy-patches copy-specs patch-specs tarballs
setup: copy-patches copy-specs patch-specs tarballs

oursrc:
	make $(oursrc)

upstream: mkdir-tree download
	make $(upstream)

all:
	make $(allsrc)

$(oursrc): rpmbuild_args += --define 'scriptsversion $(shell svnversion ${oursrcdir}/$** | tr ':' '_' | sed -e 's/-.*/0.uncommitted/')'

$(filter %.i686,$(oursrc)): %.i686: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc20-i386 --arch=i686 ${rpmbuild_args} --define="_lib lib" -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

$(filter-out %.i686,$(oursrc)): %: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc20-`uname -m` ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

$(upstream) openafs-kernel: rpmbuild_args += --define 'scriptsversion $(shell svnversion ${patches} | tr ':' '_')'

kernel: rpmbuild_args += --define 'buildid .scripts.%{scriptsversion}' --without debug --without doc

$(filter %.i686,$(upstream)): %.i686: setup patch-specs
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc20-i386 --arch=i686 ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

$(filter-out %.i686,$(upstream)): %: setup patch-specs
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/${PKG}.spec
	/usr/bin/mock -r scripts-fc20-`uname -m` ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/${PKG}-[0-9]*.src.rpm | head -1`

openafs-kernel: setup
	PATH="/usr/kerberos/sbin:/usr/kerberos/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin" \
	rpmbuild ${rpmbuild_args} -bs ${tmp_specs}/openafs*.spec
	/usr/bin/mock -r scripts-fc20-`uname -m` ${rpmbuild_args} -v --rebuild `ls -t ${out_srpms}/openafs*.src.rpm | head -1`

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
