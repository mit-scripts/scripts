# https://fedoraproject.org/wiki/PackagingDrafts/Go

Name:           scripts-proxy
Version:        0.0
Release:        0.%{scriptsversion}%{?dist}
Summary:        HTTP/SNI proxy for scripts.mit.edu

License:        GPL+
URL:            http://scripts.mit.edu/
Source0:        %{name}.tar.gz

BuildRequires:  (systemd-rpm-macros or systemd < 240)
BuildRequires:  go-rpm-macros
BuildRequires:  golang >= 1.6

%description
scripts-proxy proxies HTTP and HTTPS+SNI requests to backend servers
based on LDAP.

%global goipath github.com/mit-scripts/scripts/server/common/oursrc/scripts-proxy
%global extractdir %{name}

%gometa
%gopkg

%prep
%goprep -k

%build
%gobuild -o %{gobuilddir}/bin/scripts-proxy %{goipath}

%install
%gopkginstall
install -d %{buildroot}%{_sbindir}
install -p -m 0755 %{gobuilddir}/bin/scripts-proxy %{buildroot}%{_sbindir}/scripts-proxy
install -d %{buildroot}%{_unitdir}
install -p -m 0644 ./scripts-proxy.service %{buildroot}%{_unitdir}/scripts-proxy.service

%files
%defattr(0644, root, root)
%{_unitdir}/scripts-proxy.service
%attr(755,root,root) %{_sbindir}/scripts-proxy
%gopkgfiles

%post
%systemd_post scripts-proxy.service

%preun
%systemd_preun scripts-proxy.service

%postun
%systemd_postun_with_restart scripts-proxy.service

%changelog
* Sun Mar 8 2020 Quentin Smith - 0.0-0
- Initial packaging for scripts-proxy
