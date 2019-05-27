Summary: scripts.mit.edu php logging module
Group: Applications/System
Name: php_scripts
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildRequires: gcc
BuildRequires: php-devel
%define debug_package %{nil}

%description 

scripts.mit.edu php logging module

%prep
%setup -q -n %{name}

%build
cp php_scripts-config.m4 config.m4
phpize
./configure
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -D .libs/scripts.so $RPM_BUILD_ROOT/usr/lib64/php/modules/scripts.so

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0755, root, root)
/usr/lib64/php/modules/scripts.so

%changelog

* Fri Jul 03 2009  Mitchell Berger <mitchb@MIT.EDU> 0.00
- initial version
