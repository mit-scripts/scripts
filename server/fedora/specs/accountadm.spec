Summary: scripts.mit.edu locker administration system
Group: Applications/System
Name: accountadm
Version: 0.00
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildRequires: openafs-devel
%define debug_package %{nil}
Prereq: /usr/bin/fs, /usr/bin/pts

%description 

scripts.mit.edu locker administration system
Contains:
 - Perl script for checking whether a user is a locker admin <admof>
 - setuid C program used to start a signup request <signup-scripts-frontend>
 - Perl script that handles signup requests <signup-scripts-backend>
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure --with-fs=/usr/bin/fs --with-pts=/usr/bin/pts
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT prefix=/usr/local

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
/usr/local/etc/mbashrc
%defattr(0755, root, root)
/usr/local/bin/mbash
/usr/local/bin/admof
/usr/local/sbin/ssh-admof
/usr/local/sbin/signup-scripts-backend
%defattr(4755, signup, signup)
/usr/local/sbin/signup-scripts-frontend

%pre
groupadd -g 102 signup || [ $? -eq 9 ]
useradd -u 102 -g signup -d /afs/athena.mit.edu/contrib/scripts/signup -M signup || [ $? -eq 9 ]

%postun
userdel signup

%changelog

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- prerelease
