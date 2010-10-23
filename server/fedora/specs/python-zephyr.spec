%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python-zephyr
Version:        0.2.0
%define commit_hash c9a7f05
%define tag_hash ed65206
Release:        0.%{scriptsversion}%{?dist}
Summary:        Python access to zephyr library

Group:          Development/Languages
License:        MIT
URL:            http://github.com/ebroder/python-zephyr
Source0:        http://github.com/ebroder/python-zephyr/tarball/%{version}/ebroder-%{name}-%{version}-0-g%{commit_hash}.tar.gz
Patch1:         http://github.com/ebroder/python-zephyr/commit/944b3c3a2a2476758268d4b75b65c2ec38fa46e7.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel, python-setuptools, Pyrex, zephyr-devel, libcom_err-devel

%description
Get at the zephyr library from Python.  Woo.


%prep
%setup -q -n ebroder-%{name}-%{tag_hash}
%patch1 -p1


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
* Sun Sep 19 2010 Anders Kaseorg <andersk@mit.edu> - 0.2.0-0
- Initial RPM release

