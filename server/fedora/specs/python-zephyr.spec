Name:           python-zephyr
Version:        0.2.0
%define commit dc5ba9ee52d53e7bfd9d95a885e25c3a1889b8a7
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        1.20131014.%{scriptsversion}%{?dist}
Summary:        Python access to zephyr library

Group:          Development/Languages
License:        MIT
URL:            http://github.com/ebroder/python-zephyr
Source0:        https://github.com/ebroder/python-zephyr/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel, python-setuptools, Cython, zephyr-devel, libcom_err-devel

%description
Zephyr bindings for Python.


%prep
%setup -q -n %{name}-%{commit}


%build
CFLAGS="$RPM_OPT_FLAGS" CPPFLAGS="-I%{_includedir}/et" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{python_sitearch}/*


%changelog
* Mon Oct 14 2013 Alex Dehnert <adehnert@mit.edu> - 0.2.0-1.20131014
- Updated snapshot (Scripts-#384)

* Sun Sep 19 2010 Anders Kaseorg <andersk@mit.edu> - 0.2.0-0
- Initial RPM release

