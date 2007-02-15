Summary: scripts.mit.edu glue associated with file execution
Group: Applications/System
Name: execsys
Version: 0.00
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}

%description

scripts.mit.edu glue associated with file execution
Contains:
 - Apache configuration file <execsys.conf>
 - binfmt_misc init script <execsys-binfmt>
 - Binary for serving static content <static-cat>
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure --with-pl=/usr/bin/perl --with-php=/usr/bin/php-cgi --with-py=/usr/bin/python --with-exe=/usr/bin/mono
make SYSCATDIR=/usr/local/sbin

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT prefix=/usr/local SYSCATDIR=/usr/local/sbin

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
/etc/httpd/conf.d/execsys.conf
%defattr(0755, root, root)
/usr/local/bin/static-cat
/etc/init.d/execsys-binfmt

%post
chkconfig --add execsys-binfmt
service execsys-binfmt start

%preun
service execsys-binfmt stop
chkconfig --del execsys-binfmt

%changelog

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
