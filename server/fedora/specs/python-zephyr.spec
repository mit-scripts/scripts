%global srcname zephyr
Name:           python-%{srcname}
Version:        0.2.1
%define commit f296a349ada8574c246a0a951c9626455be902d3
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        1.20131014.%{scriptsversion}%{?dist}
Summary:        Python access to zephyr library

Group:          Development/Languages
License:        MIT
URL:            http://github.com/mit-scripts/python-zephyr
Source0:        https://github.com/mit-scripts/python-zephyr/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


%global _description %{expand:
Moira bindings for Python.}

%description %_description

%package -n python2-%{srcname}
Summary:        %{summary}
BuildRequires:  python2-devel
BuildRequires:  python2-Cython
BuildRequires:  zephyr-devel
BuildRequires:  libcom_err-devel
BuildRequires:  gcc
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname} %_description


%package -n python3-%{srcname}
Summary:        %{summary}
BuildRequires:  python3-devel
BuildRequires:  python3-Cython
BuildRequires:  zephyr-devel
BuildRequires:  libcom_err-devel
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
%doc README
%{python2_sitearch}/*

%files -n python3-%{srcname}
%doc README
%{python3_sitearch}/*


%changelog
* Wed Dec 11 2019 Quentin Smith <quentin@mit.edu> - 0.2.1
- Add support for Python 3

* Mon Oct 14 2013 Alex Dehnert <adehnert@mit.edu> - 0.2.0-1.20131014
- Updated snapshot (Scripts-#384)

* Sun Sep 19 2010 Anders Kaseorg <andersk@mit.edu> - 0.2.0-0
- Initial RPM release

