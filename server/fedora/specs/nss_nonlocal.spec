Summary: nsswitch proxy module to prevent local account spoofing
Group: System Environment/Libraries
Name: nss_nonlocal
Version: 1.6
Release: 0
URL: http://debathena.mit.edu/nss_nonlocal/
License: GPL
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This nsswitch module acts as a proxy for other nsswitch modules like hesiod,
but prevents non-local users from potentially gaining local privileges by
spoofing local UIDs and GIDs.

%prep
%setup -q -n %{name}

%build
make CFLAGS='%optflags' LDFLAGS='%optflags'

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT libdir=/%{_lib}

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc README
/%{_lib}/libnss_nonlocal.so.2

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
