Summary: scripts.mit.edu glue associated with file execution
Group: Applications/System
Name: execsys
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Requires: subversion
Requires: perl(Net::LDAP)
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildRequires: systemd-rpm-macros
BuildRequires: pkgconfig(systemd)
BuildRequires: autoconf
BuildRequires: automake
%define debug_package %{nil}

%description

scripts.mit.edu glue associated with file execution
Contains:
 - SVN and Git servers
 - binfmt_misc init script <execsys-binfmt>
See http://scripts.mit.edu/wiki for more information.

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
%{_unitdir}/execsys-binfmt.service
%{_unitdir}/scripts-svn.socket
%{_unitdir}/scripts-svn@.service
%{_unitdir}/scripts-git.socket
%{_unitdir}/scripts-git@.service
%{_unitdir}/scripts-local-smtp.socket
%{_unitdir}/scripts-local-smtp@.service
%defattr(0755, root, root)
/usr/sbin/ldapize.pl
/usr/sbin/svnproxy.pl
/usr/sbin/gitproxy.pl
/usr/sbin/local-smtp-proxy
/usr/libexec/scripts-trusted/svn
/usr/libexec/scripts-trusted/git

%post
%systemd_post execsys-binfmt.service
%systemd_post execsys-svn.socket
%systemd_post execsys-svn@.service
%systemd_post execsys-git.socket
%systemd_post execsys-git@.service
%systemd_post execsys-local-smtp.socket
%systemd_post execsys-local-smtp@.service

%preun
%systemd_preun execsys-binfmt.service
%systemd_preun execsys-svn.socket
%systemd_preun execsys-svn@.service
%systemd_preun execsys-git.socket
%systemd_preun execsys-git@.service
%systemd_preun execsys-local-smtp.socket
%systemd_preun execsys-local-smtp@.service

%postun
%systemd_postun_with_restart execsys-binfmt.service
%systemd_postun_with_restart execsys-svn.socket
%systemd_postun_with_restart execsys-svn@.service
%systemd_postun_with_restart execsys-git.socket
%systemd_postun_with_restart execsys-git@.service
%systemd_postun_with_restart execsys-local-smtp.socket
%systemd_postun_with_restart execsys-local-smtp@.service

%changelog
* Mon Jun 24 2019  Quentin Smith <quentin@mit.edu>
- Brave new systemd world

* Wed Dec 31 2008  Quentin Smith <quentin@mit.edu>
- don't stop execsys on package updates

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
