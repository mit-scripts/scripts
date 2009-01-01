Summary: scripts.mit.edu glue associated with file execution
Group: Applications/System
Name: execsys
Version: 0.SVNVERSION_TO_UPDATE
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Requires: xinetd
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
./configure --prefix=/usr/local --with-pl=/usr/bin/perl --with-php=/usr/bin/php-cgi --with-py=/usr/bin/python --with-exe=/usr/bin/mono
make SYSCATDIR=/usr/local/sbin

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT SYSCATDIR=/usr/local/sbin

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
/etc/httpd/conf.d/execsys.conf
%defattr(0755, root, root)
/usr/local/bin/static-cat
/etc/init.d/execsys-binfmt
/usr/local/sbin/ldapize.pl
/usr/local/sbin/svnproxy.pl
/usr/libexec/scripts-trusted/svn
/etc/xinetd.d/scripts-svn
/usr/local/sbin/gitproxy.pl
/usr/libexec/scripts-trusted/git
/etc/xinetd.d/scripts-git

%post
chkconfig --add execsys-binfmt
service execsys-binfmt start
service xinetd reload

%preun
service execsys-binfmt stop
chkconfig --del execsys-binfmt

%postun
service xinetd reload

%changelog

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
