Summary:        whoisd for <scripts.mit.edu> (virtualhost aware)
Group:			Applications/System
Name:           whoisd
Version:        0.00
Release:        0
Vendor:			The scripts.mit.edu Team (scripts@mit.edu)
URL:			http://scripts.mit.edu
License:        GPL
Source0:        %{name}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define debug_package %{nil}

#BuildRequires:  make
Requires:       python-twisted-core

%description


%prep
%setup -q -n %{name}

%build
./configure

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT exec_prefix=/usr/local

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644,root,root,-)
/usr/local/libexec/whoisd.tac
%defattr(0600,root,root)
/etc/cron.d/whoisd

%changelog

* Tue Jun 03 2008 Joe Presbrey <presbrey@mit.edu> 0.00
- prerelease
