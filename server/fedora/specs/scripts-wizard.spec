Name:           scripts-wizard
Version:        0
Release:        1.%{scriptsversion}%{?dist}
Summary:        Symlink for the scripts.mit.edu wizard autoinstaller system

Group:          Development/Tools
License:        MIT
URL:            http://scripts.mit.edu
Source0:        %{name}.tar.gz

%define debug_package %{nil}

%description

Symlink for the scripts.mit.edu wizard autoinstaller system

%prep
%setup -q -n %{name}

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/local/bin
ln -s /afs/athena.mit.edu/contrib/scripts/wizard/bin/wizard %{buildroot}/usr/local/bin/wizard

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/local/bin/wizard

%changelog
* Thu Mar 04 2010 Mitchell Berger <mitchb@mit.edu> - 0-1.1503
- Initial release

