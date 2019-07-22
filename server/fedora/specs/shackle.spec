Summary: DBL-checking DNS server
Group: Applications/System
Name: shackle
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Requires: python3
Requires: python3dist(twisted)
Requires: libpsl
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildRequires: systemd-rpm-macros
BuildRequires: pkgconfig(systemd)
BuildRequires: autoconf
BuildRequires: automake
%define debug_package %{nil}

%description

DBL-checking DNS server

In the default configuration, checks each domain against Spamhaus. If
the doamin is found in the Spamhaus DBL, a syslog is emitted to
authpriv.

In either case, the query is forwarded to 127.0.0.1:54 and the correct
response is returned.

%prep
%setup -q -n %{name}

%build
autoreconf -fvi
%configure
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
%{_unitdir}/shackle.service
%{_unitdir}/shackle.socket
%defattr(0755, root, root)
%{_sbindir}/shackle

%post
%systemd_post shackle.service
%systemd_post shackle.socket

%preun
%systemd_preun shackle.service
%systemd_preun shackle.socket

%postun
%systemd_postun_with_restart shackle.service
%systemd_postun_with_restart shackle.socket

%changelog
* Mon Jul 22 2019  Quentin Smith <quentin@mit.edu>
- New package
