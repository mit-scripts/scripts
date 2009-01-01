Summary: scripts.mit.edu logview program
Group: Applications/System
Name: logview
Version: 0.SVNVERSION_TO_UPDATE
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}

%description 

scripts.mit.edu logview program
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT prefix=/usr/local

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%pre
useradd logview

%postun
userdel logview

%files
%defattr(0755, root, root)
/usr/local/bin/logview.pl
%defattr(4755, logview, root)
/usr/local/bin/logview

%changelog

* Tue Jan 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- prerelease
