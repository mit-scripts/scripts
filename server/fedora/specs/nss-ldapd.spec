#
# spec file for package nss_ldap (Version 256)
#
# Copyright (c) 2007 SUSE LINUX Products GmbH, Nuernberg, Germany.
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild

Name:           nss-ldapd
BuildRequires:  db4-devel krb5-devel openldap-devel autoconf automake libtool
License:        LGPL v2.1 or later
Group:          Productivity/Networking/LDAP/Clients
Autoreqprov:    on
Version:        0.6.4
Release:        2.4
Summary:        NSS LDAP Daemon and Module
URL:            http://ch.tudelft.nl/~arthur/nss-ldapd/
Source:         nss-ldapd-%{version}.tar.bz2
Source1:        rc.nslcd
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Nss-ldapd is a fork of the nss_ldap package by PADL Software Pty Ltd.. This
fork was done to implement some structural design changes. These changes were
needed because there are some issues with the original design.

Authors:
--------
    Luke Howard <lukeh@padl.com>
    West Consulting <info@west.nl>
    Arthur de Jong <arthur@ch.tudelft.nl>

%prep
%setup -q
cp -v %{S:1} .

%build
%{?suse_update_config:%{suse_update_config -f}}
autoreconf
CFLAGS="$RPM_OPT_FLAGS" \
CPPFLAGS="-I/usr/include/sasl" \
./configure --prefix=/usr \
            --mandir=%{_mandir} \
	    --enable-schema-mapping \
	    --enable-paged-results \
            --enable-configurable-krb5-ccname-gssapi \
	    --libdir=/%{_lib} \
	    --sysconfdir=/etc 
make

%install
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
mkdir -p $RPM_BUILD_ROOT/usr/sbin/
install -m 755 rc.nslcd $RPM_BUILD_ROOT/etc/init.d/nslcd
ln -sf ../../etc/init.d/nslcd $RPM_BUILD_ROOT/usr/sbin/rcnslcd
make DESTDIR=$RPM_BUILD_ROOT install
mkdir -p $RPM_BUILD_ROOT/var/run/nslcd
install -m 644 man/nss-ldapd.conf.5 $RPM_BUILD_ROOT/usr/share/man/man5
install -m 644 man/nslcd.8 $RPM_BUILD_ROOT/usr/share/man/man8

%clean
rm -fr $RPM_BUILD_ROOT

%post
/sbin/ldconfig

%preun
%stop_on_removal nslcd

%postun 
/sbin/ldconfig
%restart_on_update nslcd
%insserv_cleanup

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README
/%{_lib}/libnss_ldap.so.2
%doc %{_mandir}/man5/*
%doc %{_mandir}/man8/*
%config(noreplace) /etc/nss-ldapd.conf
%config /etc/init.d/nslcd
/usr/sbin/rcnslcd
%dir /var/run/nslcd
/usr/sbin/nslcd

%changelog
* Wed Dec 31 2008  <quentin@mit.edu> - 0.6.4-2.4
- port from openSUSE to Fedora
* Wed Aug  6 2008 rhafer@suse.de
- rename init script to nslcd to match the name of the daemon
  binary
* Wed Aug  6 2008 rhafer@suse.de
- updated to nss-ldapd-0.6.4
  * fix for the tls_checkpeer option
  * fix incorrect test for ssl option in combination with ldaps:// URIs
  * improvements to Active Directory sample configuration
  * implement looking up search base in rootDSE of LDAP server
* Mon Jun 16 2008 rhafer@suse.de
- updated to nss-ldapd-0.6.3
  * retry connection and search if getting results failed with connection
  * problems (some errors only occur when getting the results, not when
    starting the search)
  * add support for groups with up to around 150000 members (assuming user
    names on average are a little under 10 characters)
  * problem with possible SIGPIPE race condition was fixed by using send()
    instead of write()
  * add uid and gid configuration keywords that set the user and group of the
    nslcd daemon
  * add some documentation on supported group to member mappings
  * add sanity checking to code for when clock moves backward
  * log messages now include a session id that makes it easier to track errors
    to requests (especially useful in debugging mode)
  * miscellaneous portability improvements
  * increase buffers and timeouts to handle large lookups more gracefully
  * implement SASL authentication based on a patch by Dan White
  * allow more characters in user and group names
* Mon Feb 11 2008 rhafer@suse.de
- updated to nss-ldapd-0.6
* Mon Jan  7 2008 rhafer@suse.de
- updated to nss-ldapd-0.5
* Fri Nov 16 2007 rhafer@suse.de
- Added patches configuration by SRV records
- Added patch to re-enable use_sasl and krb5_ccname
* Mon Oct 29 2007 rhafer@suse.de
- updated to nss-ldapd-0.4.1
* Thu Oct 11 2007 rhafer@suse.de
- updated to nss-ldapd-0.4
* Thu Aug 30 2007 rhafer@suse.de
- updated to nss-ldapd-0.3
* Mon Jul 30 2007 rhafer@suse.de
- initial version for nss-ldapd-0.2.1
