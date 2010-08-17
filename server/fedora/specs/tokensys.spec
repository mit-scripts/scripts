Summary: scripts.mit.edu AFS administration system
Group: Applications/System
Name: tokensys
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}
Prereq: /usr/kerberos/bin/kinit, /usr/bin/aklog

%description

scripts.mit.edu AFS administration system
Contains:
 - A shell script for renewing the scripts AFS credentials <renew>
 - A crontab for calling the renew script <crontab>
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure --with-kinit=/usr/kerberos/bin/kinit --with-aklog=/usr/bin/aklog

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -D renew $RPM_BUILD_ROOT/home/afsagent/renew
install -D crontab $RPM_BUILD_ROOT/etc/cron.d/afsagent

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0600, root, root)
/etc/cron.d/afsagent
%defattr(0755, afsagent, afsagent)
/home/afsagent/renew

%pre
groupadd -g 101 afsagent || [ $? -eq 9 ]
useradd -u 101 -g 101 afsagent || [ $? -eq 9 ]

%postun
if [ "$1" = "0" ] ; then
   userdel -r afsagent
fi

%changelog
* Tue Aug 17 2010  Geoffrey Thomas <geofft@mit.edu>
- aklog csail as well

* Wed Dec 31 2008  Quentin Smith <quentin@mit.edu>
- only remove afsagent user on erase
- ignore preexisting user

* Wed Apr 11 2007  Joe Presbrey <presbrey@mit.edu>
- crontab moved system-wide (/etc/cron.d) to isolate from fail-over cron service

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
