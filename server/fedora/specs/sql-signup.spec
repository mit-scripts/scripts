Summary:        Signup interface to <sql.mit.edu> for <scripts.mit.edu>.
Group:			Applications/System
Name:           sql-signup
Version:        0.%{scriptsversion}
Release:        0
Vendor:			The scripts.mit.edu Team (scripts@mit.edu)
URL:			http://scripts.mit.edu
License:        GPL
Source0:        %{name}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define debug_package %{nil}

BuildRequires:  make
Requires:       pam, usermode

%description


%prep
%setup -q -n %{name}

%build


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT prefix=/usr/local

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%defattr(755,root,root,-)
%{_bindir}/sql-signup
%{_sbindir}/sql-signup
%defattr(644,root,root,-)
%config /etc/pam.d/sql-signup
%config /etc/security/console.apps/sql-signup

%changelog

* Fri Jan 26 2007 Joe Presbrey <presbrey@mit.edu> 0.00
- prerelease
