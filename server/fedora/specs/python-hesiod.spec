Name:           python-hesiod
Version:        0.2.10
%define commit 2b11f727fe934efe8935ac3543fe538d14b8fafe
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        0.%{scriptsversion}%{?dist}
Summary:        Python access to zephyr library

Group:          Development/Languages
License:        MIT
URL:            https://github.com/ebroder/python-hesiod
Source0:        https://github.com/ebroder/python-hesiod/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python2-devel, python-setuptools, Pyrex, hesiod-devel

%description
Hesiod bindings for Python.


%prep
%setup -q -n %{name}-%{commit}


%build
CFLAGS="$RPM_OPT_FLAGS" CPPFLAGS="-I%{_includedir}/et" %{__python2} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{python_sitearch}/*


%changelog
* Sun Oct 13 2013 Alex Dehnert <adehnert@mit.edu> - 0.2.10
- Initial RPM release

