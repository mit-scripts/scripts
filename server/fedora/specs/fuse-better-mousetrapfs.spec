Summary:        FUSE-Filesystem that logs and kills any accessors
Group:          System Environment/Base
Name:           fuse-better-mousetrapfs
Version:        0
Release:        1.%{scriptsversion}%{?dist}
Vendor:         The scripts.mit.edu Team (scripts@mit.edu)
URL:            http://scripts.mit.edu
License:        BSD
Source0:        %{name}.tar.gz
BuildArch:	noarch

%define debug_package %{nil}

Requires:       fuse >= 2.2
Requires:       fuse-python

%description
This is a FUSE-filesystem client which logs and kills any accessors.
It is useful for detecting compromised accounts which are performing
filesystem scans.

%prep
%setup -q -n %{name}

%build

%install
rm -rf %{buildroot}
install -D better-mousetrapfs %{buildroot}/usr/local/sbin/better-mousetrapfs

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/local/sbin/better-mousetrapfs

%changelog
* Mon Mar 26 2012 Edward Z. Yang <ezyang@mit.edu> - 0-1.2150
- Initial release.
