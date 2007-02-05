Summary: scripts.mit.edu logview program
Group: Applications/System
Name: logview
Version: 0.00
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}
Requires: httpd

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
groupadd logview
chgrp logview /var/log/httpd

%post
chgrp logview /usr/local/bin/logview
chmod g+s /usr/local/bin/logview

%postrm
groupdel logview
chgrp root /var/log/httpd

%files
%defattr(0755, root, root)
/usr/local/bin/logview.pl
/usr/local/bin/logview

%changelog

* Tue Jan 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- prerelease
