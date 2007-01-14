Summary: scripts.mit.edu locker administration system
Group: Applications/System
Name: accountadm
Version: 0.00
Release: scripts
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
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
install -D modbashrc $RPM_BUILD_ROOT/usr/local/etc/modbashrc
install -D modbash $RPM_BUILD_ROOT/usr/local/bin/modbash
install -D admof $RPM_BUILD_ROOT/usr/local/sbin/admof
install -D signup-scripts-frontend $RPM_BUILD_ROOT/usr/local/sbin/signup-scripts-frontend
install -D signup-scripts-backend $RPM_BUILD_ROOT/usr/local/sbin/signup-scripts-backend

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
/usr/local/etc/modbashrc
%defattr(0755, root, root)
/usr/local/bin/modbash
/usr/local/sbin/admof
/usr/local/sbin/signup-scripts-backend
%defattr(4755, signup, signup)
/usr/local/sbin/signup-scripts-frontend

%pre
groupadd signup
useradd -g signup signup

%post
cat >>/etc/sudoers <<END
signup  ALL=(root) NOPASSWD: /usr/sbin/useradd
signup  ALL=(root) NOPASSWD: /usr/sbin/groupadd
signup  ALL=(root) NOPASSWD: /usr/sbin/setquota
END
chmod 0440 /etc/sudoers

%preun
touch /etc/sudoers.tmp
chmod 600 /etc/sudoers.tmp
grep -v "^signup" /etc/sudoers > /etc/sudoers.tmp
mv /etc/sudoers.tmp /etc/sudoers

%postun
userdel -r signup

%changelog

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- prerelease
