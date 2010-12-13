Summary: scripts.mit.edu base packages
Group: Applications/System
Name: scripts-base
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
Requires: accountadm, execsys, scripts-kmod-openafs, scripts-krb5-libs, scripts-httpd, scripts-mod_ssl, openafs, scripts-openafs-client, scripts-openafs-authlibs, scripts-openafs-devel, scripts-openafs-krb5, openafs-docs, scripts-openssh-server, sql-signup, tokensys, whoisd, logview, nss-ldapd, php_scripts, zephyr, httpdmods, nss_nonlocal, scripts-389-ds
%define debug_package %{nil}

%description 

scripts.mit.edu base package
Contains:
 - Dependencies to install rpms required for base scripts functionality
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}

%build

%install

%clean

%files

%changelog
* Thu Jan  1 2009  Quentin Smith <quentin@mit.edu>
- prerelease
