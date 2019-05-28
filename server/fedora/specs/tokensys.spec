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
Prereq: /usr/bin/kinit, /usr/bin/aklog
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
BuildRequires: systemd-units

%description

scripts.mit.edu AFS administration system
Contains:
 - A shell script for renewing the scripts AFS credentials <renew>
 - A shell script for configuring scripts AFS <scripts-afsagent-startup>
 - systemd units for running the above
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure --with-kinit=/usr/bin/kinit --with-klist=/usr/bin/klist --with-aklog=/usr/bin/aklog --with-fs=/usr/bin/fs

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -D renew $RPM_BUILD_ROOT/home/afsagent/renew
install -D scripts-afsagent-startup $RPM_BUILD_ROOT/usr/local/libexec/scripts-afsagent-startup
install -D scripts-afsagent-startup.service $RPM_BUILD_ROOT%{_unitdir}/scripts-afsagent-startup.service
install -D scripts-afsagent.service $RPM_BUILD_ROOT%{_unitdir}/scripts-afsagent.service
install -D scripts-afsagent.timer $RPM_BUILD_ROOT%{_unitdir}/scripts-afsagent.timer

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644,root,root)
%{_unitdir}/*.service
%{_unitdir}/*.timer
%defattr(0755, afsagent, afsagent)
/home/afsagent/renew
/usr/local/libexec/scripts-afsagent-startup

%pre
groupadd -g 101 afsagent || [ $? -eq 9 ]
useradd -u 101 -g 101 afsagent || [ $? -eq 9 ]

%post
/bin/systemctl enable scripts-afsagent-startup.service >/dev/null 2>&1 || :
/bin/systemctl enable scripts-afsagent.service >/dev/null 2>&1 || :
/bin/systemctl enable scripts-afsagent.timer >/dev/null 2>&1 || :

if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable scripts-afsagent-startup.service > /dev/null 2>&1 || :
    /bin/systemctl --no-reload disable scripts-afsagent.service > /dev/null 2>&1 || :
    /bin/systemctl --no-reload disable scripts-afsagent.timer > /dev/null 2>&1 || :
    /bin/systemctl stop scripts-afsagent-startup.service > /dev/null 2>&1 || :
    /bin/systemctl stop scripts-afsagent.service > /dev/null 2>&1 || :
    /bin/systemctl stop scripts-afsagent.timer > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart scripts-afsagent.service >/dev/null 2>&1 || :
fi

if [ "$1" = "0" ] ; then
   userdel -r afsagent
fi

%changelog
* Mon Nov 21 2011  Quentin Smith <quentin@mit.edu>
- add systemd units
- remove crontab

* Tue Aug 17 2010  Geoffrey Thomas <geofft@mit.edu>
- aklog csail as well

* Wed Dec 31 2008  Quentin Smith <quentin@mit.edu>
- only remove afsagent user on erase
- ignore preexisting user

* Wed Apr 11 2007  Joe Presbrey <presbrey@mit.edu>
- crontab moved system-wide (/etc/cron.d) to isolate from fail-over cron service

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
