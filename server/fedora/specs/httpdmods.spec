Summary: scripts.mit.edu custom apache modules
Group: Applications/System
Name: httpdmods 
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
%define debug_package %{nil}

%description 

scripts.mit.edu custom apache modules
Contains:
 - module to do authentication based on SSL certificates <mod_auth_sslcert>
 - module to do authorization based on Athena AFS groups <mod_authz_afsgroup>
 - module to enable optional authentication <mod_auth_optional>
 - module to get vhosts from LDAP, taken from Debian <mod_vhost_ldap>
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build
./configure CFLAGS="-I/usr/include/httpd -I/usr/include/apr-1"
make

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -D .libs/mod_auth_sslcert.so $RPM_BUILD_ROOT/usr/lib64/httpd/modules/mod_auth_sslcert.so
install -D .libs/mod_authz_afsgroup.so $RPM_BUILD_ROOT/usr/lib64/httpd/modules/mod_authz_afsgroup.so
install -D .libs/mod_auth_optional.so $RPM_BUILD_ROOT/usr/lib64/httpd/modules/mod_auth_optional.so
install -D .libs/mod_vhost_ldap.so $RPM_BUILD_ROOT/usr/lib64/httpd/modules/mod_vhost_ldap.so

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0755, root, root)
/usr/lib64/httpd/modules/mod_auth_sslcert.so
/usr/lib64/httpd/modules/mod_authz_afsgroup.so
/usr/lib64/httpd/modules/mod_auth_optional.so
/usr/lib64/httpd/modules/mod_vhost_ldap.so

%changelog

* Sun Jan 13 2006  Jeff Arnold <jbarnold@MIT.EDU> 0.00
- initial prerelease version
