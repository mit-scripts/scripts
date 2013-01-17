Name:		scripts-munin-plugins
Version:	0
Release:	1.%{scriptsversion}%{?dist}
Summary:	scripts.mit.edu munin monitoring plugins

License:	GPLv2+
URL:		http://scripts.mit.edu
Source0:	%{name}.tar.gz

Requires:	munin-node
Requires:	perl(Net::LDAP)

BuildArch:	noarch


%description
A collection of scripts.mit.edu munin plugins for monitoring, beyond
the standard plugins provided by munin-node.


%define debug_package %{nil}


%prep
%setup -q -n %{name}


%build
# This package is perl, nothing to configure or make


%install
rm -rf $RPM_BUILD_ROOT
%make_install


%files
%defattr(-,root,root,-)
/usr/share/munin/plugins/389ds
%doc


%changelog
* Thu Jan 17 2013 Alexander Chernyakhovsky <achernya@mit.edu> - 0-1
- Initial packaging of scripts-munin-plugins

