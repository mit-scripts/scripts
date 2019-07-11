Summary:   whoisd for <scripts.mit.edu> (virtualhost aware)
Group:     Applications/System
Name:      whoisd
Version:   0.%{scriptsversion}
Release:   2
Vendor:    The scripts.mit.edu Team (scripts@mit.edu)
URL:       http://scripts.mit.edu
License:   GPL
Source0:   %{name}.tar.gz

%define debug_package %{nil}

Requires:      python-twisted-core
BuildRequires: systemd-rpm-macros

%description


%prep
%setup -q -n %{name}

%build
./configure

%install
make install DESTDIR=$RPM_BUILD_ROOT exec_prefix=/usr/local

%post
%systemd_post scripts-whoisd.service

%preun
%systemd_preun scripts-whoisd.service

%postun
%systemd_postun_with_restart scripts-whoisd.service

%files
%defattr(0644,root,root,-)
/usr/local/libexec/whoisd.tac
%defattr(0644,root,root)
%{_unitdir}/scripts-whoisd.service

%changelog
* Thu Jul 11 2019 Quentin Smith <quentin@mit.edu> 0-2
- use systemd rpm scriptlets

* Thu Aug 25 2011 Alexander Chernyakhovsky <achernya@mit.edu> 0-1
- package systemd service file

* Tue Jun 03 2008 Joe Presbrey <presbrey@mit.edu> 0.00
- prerelease
