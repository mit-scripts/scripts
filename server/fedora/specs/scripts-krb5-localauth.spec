Summary: scripts.mit.edu krb5 localauth plugin
Group: Applications/System
Name: scripts-krb5-localauth
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
BuildRequires: krb5-devel
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
%define debug_package %{nil}

%description 

scripts.mit.edu krb5 localauth plugin
Contains:
 - krb5 plugin that runs admof to check permissions
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
autoreconf -fvi
%configure
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0755, root, root)
/usr/lib64/libscripts-krb5-localauth.*

%changelog
* Sun May 26 2019  Quentin Smith <quentin@MIT.EDU> 0.00
- Initial release
