%global srcname hesiod
Name:           python-%{srcname}
Version:        0.2.11
%define commit 583fc21cee08baaf5117ed8045bf18a9252eba84
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        1.%{scriptsversion}%{?dist}
Summary:        Python access to hesiod library

Group:          Development/Languages
License:        MIT
URL:            https://github.com/mit-scripts/python-hesiod
Source0:        https://github.com/mit-scripts/python-hesiod/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%global _description %{expand:
Hesiod bindings for Python.}

%description %_description

%package -n python2-%{srcname}
Summary:        %{summary}
BuildRequires:  python2-devel
BuildRequires:  python2-Cython
BuildRequires:  hesiod-devel
BuildRequires:  gcc
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname} %_description


%package -n python3-%{srcname}
Summary:        %{summary}
BuildRequires:  python3-devel
BuildRequires:  python3-Cython
BuildRequires:  hesiod-devel
BuildRequires:  gcc
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname} %_description


%prep
%autosetup -n %{name}-%{commit}


%build
%py2_build
%py3_build

%install
%py2_install
%py3_install
 
%files -n python2-%{srcname}
%license COPYING
%doc README
%{python2_sitearch}/hesiod.*
%{python2_sitearch}/_hesiod.so
%{python2_sitearch}/PyHesiod-*.egg-info/

%files -n python3-%{srcname}
%license COPYING
%doc README
%{python3_sitearch}/hesiod.py
%{python3_sitearch}/__pycache__/*
%{python3_sitearch}/_hesiod.*.so
%{python3_sitearch}/PyHesiod-*.egg-info/


%changelog
* Mon Dec 9 2019 Quentin Smith <quentin@mit.edu> - 0.2.11
- Add support for Python 3

* Sun Oct 13 2013 Alex Dehnert <adehnert@mit.edu> - 0.2.10
- Initial RPM release

