Summary: scripts.mit.edu locker administration system
Group: Applications/System
Name: accountadm
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildRequires: scripts-openafs-devel, scripts-openafs-authlibs-devel
BuildRequires: hesiod
BuildRequires: openldap-clients
BuildRequires: krb5-devel
BuildRequires: sudo
Requires: hesiod
Requires: openldap-clients
Requires: sudo
%define debug_package %{nil}
Prereq: /usr/bin/fs, /usr/bin/pts

%description 

scripts.mit.edu locker administration system
Contains:
 - Perl script for checking whether a user is a locker admin <admof>
 - Perl script that handles signup requests <signup-scripts-backend>
 - vhostadd,vhostedit: admin tools for adding and editing virtualhosts
 - cronload: userspace tool for setting crontab from Athena
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
/usr/local/bin/cronload
/usr/local/sbin/ssh-admof
/usr/local/sbin/signup-scripts-backend
/usr/local/sbin/vhostadd
/usr/local/sbin/vhostedit
/usr/local/sbin/ldap-backup
/usr/local/sbin/get-homedirs

%pre
groupadd -g 102 signup || [ $? -eq 9 ]
useradd -u 102 -g signup -d /afs/athena.mit.edu/contrib/scripts/signup -M signup || [ $? -eq 9 ]

%postun
if [ "$1" = "0" ] ; then
   userdel signup
fi

%changelog
* Wed Dec 31 2008  Quentin Smith <quentin@mit.edu> - 0.917-0
- don't delete signup user on upgrades

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- prerelease
