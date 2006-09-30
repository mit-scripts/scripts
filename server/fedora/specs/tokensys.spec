Summary: scripts.mit.edu AFS administration system
Group: Applications/System
Name: tokensys
Version: 0.00
Release: scripts
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}

%description 

scripts.mit.edu AFS administration system
Contains:
 - A shell script for renewing the system's AFS credentials <renew>
 - A crontab for calling the renew script <crontab> 
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -D renew $RPM_BUILD_ROOT/home/afsagent/renew
install -D crontab $RPM_BUILD_ROOT/home/afsagent/crontab

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, afsagent, afsagent)
/home/afsagent/crontab
%defattr(0755, afsagent, afsagent)
/home/afsagent/renew

%pre
groupadd -g 101 afsagent
useradd -u 101 -g 101 afsagent

%post
crontab -u afsagent /home/afsagent/crontab

%preun
crontab -u afsagent -r

%postun
userdel -r afsagent

%changelog

* Sat Sep 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
