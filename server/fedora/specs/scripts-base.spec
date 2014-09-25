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
%define all_archs() %1%{?_isa}, %{?__isa_name: %1(%{__isa_name}-32)}
Requires: accountadm
Requires: execsys
Requires: scripts-bash
Requires: scripts-dkms-openafs
Requires: %{all_archs scripts-krb5-libs}
Requires: scripts-httpd
Requires: scripts-mod_ssl
Requires: scripts-openafs-client
Requires: scripts-openafs-authlibs
Requires: scripts-openafs-devel
Requires: scripts-openafs-krb5
Requires: scripts-openssh-server
Requires: scripts-static-cat
Requires: sql-signup
Requires: tokensys
Requires: whoisd
Requires: logview
Requires: fuse-better-mousetrapfs
Requires: %{all_archs nss-pam-ldapd}
Requires: php_scripts
Requires: zephyr
Requires: %{all_archs zephyr-libs}
Requires: httpdmods
Requires: %{all_archs nss_nonlocal}
Requires: scripts-munin-plugins
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
