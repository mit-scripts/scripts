Name:           python-moira
Version:        4.3.0
%define commit dd03ce70d348d6f569729fcc9173429a5ec8a84d
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        0.%{scriptsversion}%{?dist}
Summary:        Python access to zephyr library

Group:          Development/Languages
License:        MIT
URL:            https://github.com/ebroder/python-moira
Source0:        https://github.com/ebroder/python-moira/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python2-devel, python-setuptools, Pyrex, libmoira-devel, libmrclient-devel

%description
Moira bindings for Python.


%prep
%setup -q -n %{name}-%{commit}


%build
CFLAGS="$RPM_OPT_FLAGS" CPPFLAGS="-I%{_includedir}/et" %{__python2} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm $RPM_BUILD_ROOT/usr/bin/qy

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{python_sitearch}/*


%changelog
* Sun Oct 13 2013 Alex Dehnert <adehnert@mit.edu> - 4.3.0
- Initial RPM release

