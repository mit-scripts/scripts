Name:           scripts-ldap-base
Version:        1.1
Release:        1%{?dist}
Summary:        Scripts LDAP Server metapackage

License:        GPLv2
URL:            http://scripts.mit.edu/

BuildArch:      noarch

Requires:       389-ds-base
Requires:       chrony
Requires:       emacs-nox
Requires:       krb5-workstation
Requires:       net-tools
Requires:       openssh-clients
Requires:       openssh-server
Requires:       rpmdevtools
Requires:       screen
Requires:       subversion
Requires:       yum-utils

%description
Base package for scripts.mit.edu LDAP servers. Installing this package
should install all dependencies for running a full scripts-ldap
cluster member.


%files


%changelog
* Sat Aug 23 2014 Alex Chernyakhovsky <achernya@mit.edu> 1.1-1
- Add yum-utils and chrony

* Sat Aug 23 2014 Alex Chernyakhovsky <achernya@mit.edu> 1.0-1
- Initial packaging.
