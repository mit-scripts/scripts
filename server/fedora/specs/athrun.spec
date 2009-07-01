Summary: scripts.mit.edu version of Athena athrun utility
Group: Applications/System
Name: athrun
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: MIT
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}

%description 

scripts.mit.edu version of Athena athrun utility

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

%files
%defattr(0755, root, root)
/usr/local/bin/athrun

%changelog
* Wed Jul 01 2009  Mitchell Berger <mitchb@MIT.EDU> 0.00
- Initial version
