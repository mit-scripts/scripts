Summary: scripts.mit.edu logview program
Group: Applications/System
Name: logview
Version: 1.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildArch: noarch

%define debug_package %{nil}

%description 
scripts.mit.edu logview program
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/%{_bindir}/
cp logview %{buildroot}/%{_bindir}/logview

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%pre
useradd logview || [ $? -eq 9 ]
chmod 710 /home/logview

%postun
if [ "$1" = "0" ] ; then
   userdel logview
fi

%files
%{_bindir}/logview

%changelog
* Fri Aug 29 2014 Alexander Chernyakhovsky <achernya@mit.eduu> - 1.2601-0
- logview is now journalctl

* Wed Dec 31 2008  Quentin Smith <quentin@mit.edu>
- ignore preexisting user

* Wed Dec 31 2008  Quentin Smith <quentin@mit.edu> - 0.917-0
- don't delete logview user on upgrades

* Tue Jan 30 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- prerelease
