Summary: nsswitch proxy module to prevent local account spoofing
Group: System Environment/Libraries
Name: nss_nonlocal
Version: 2.0
Release: 1
URL: http://debathena.mit.edu/nss_nonlocal/
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
License: LGPLv2+
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires(pre): shadow-utils

%description
This nsswitch module acts as a proxy for other nsswitch modules like hesiod,
but prevents non-local users from potentially gaining local privileges by
spoofing local UIDs and GIDs.

%prep
%setup -q -n %{name}

cat >find_requires.sh <<EOF
#!/bin/sh
%{__find_requires} | grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_requires.sh
%define _use_internal_dependency_generator 0
%define __find_requires %{_builddir}/%{buildsubdir}/find_requires.sh

%build
autoreconf -i
%configure --libdir=/%{_lib}
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc README
/%{_lib}/libnss_nonlocal.so.*

%pre
getent passwd nss-nonlocal-users >/dev/null || \
    useradd -r -g nobody -d / -s /sbin/nologin \
    -c 'Magic user for local group whitelist' nss-nonlocal-users
getent group nss-local-users || groupadd -r nss-local-users
getent group nss-nonlocal-users || groupadd -r nss-nonlocal-users
exit 0

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%changelog

* Tue Mar 29 2011 Anders Kaseorg <andersk@mit.edu> 2.0-1
- New upstream version.

* Sun May  2 2010 Anders Kaseorg <andersk@mit.edu> 1.11-1
- New upstream version.

* Fri Mar 12 2010 Mitchell Berger <mitchb@mit.edu> 1.9-1
- Per Fedora packaging guidelines, don't ever remove groups.
- Rebuild to ensure that the nss-nonlocal-users group is added, even if it was
  previously rejected by a buggy groupadd with an incorrect name length limit.

* Thu May  8 2008 Anders Kaseorg <andersk@mit.edu> 1.6-0
- Initial RPM release.
