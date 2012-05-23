Name:           python-afs
Version:        0.1.1
%define commit_hash dceee3da
%define tag_hash fb29c26
Release:        0.%{scriptsversion}%{?dist}
Summary:        Python access to AFS library

Group:          Development/Languages
License:        GPL
URL:            http://github.com/ebroder/pyafs
Source0:        http://github.com/ebroder/pyafs/tarball/%{version}/ebroder-%{name}-%{version}-0-g%{commit_hash}.tar.gz
Patch1:         https://github.com/ebroder/pyafs/commit/94a09d55edd7d3c1b53424ee1a39245db751c5e9.patch
Patch2:         https://github.com/ebroder/pyafs/commit/d6425bd9fa52034a2a62ed95c8fec8cbcfd2707d.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel, python-setuptools, Cython, openafs-devel, openafs-authlibs-devel, krb5-devel

%description
Get at AFS from Python.


%prep
%setup -q -n ebroder-pyafs-%{tag_hash}
%patch1 -p1
%patch2 -p1


%build
CFLAGS="$RPM_OPT_FLAGS" CPPFLAGS="-I%{_includedir}/et" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{python_sitearch}/*


%changelog
* Thu Dec 15 2011 Alex Dehnert <adehnert@mit.edu> - 0.1.1
- Initial RPM release

