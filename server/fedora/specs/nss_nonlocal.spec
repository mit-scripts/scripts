Summary: nsswitch proxy module to prevent local account spoofing
Group: System Environment/Libraries
Name: nss_nonlocal
Version: 1.7
Release: 0
URL: http://debathena.mit.edu/nss_nonlocal/
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
License: GPL
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

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
groupadd -r nss-local-users || :
groupadd -r nss-nonlocal-users || :

%post
/sbin/ldconfig

%postun
/sbin/ldconfig
test "$1" != 0 || groupdel nss-local-users || :
test "$1" != 0 || groupdel nss-nonlocal-users || :

%changelog

* Thu May  8 2008 Anders Kaseorg <andersk@mit.edu> 1.6-0
- Initial RPM release.
