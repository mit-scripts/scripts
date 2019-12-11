%global srcname moira
Name:           python-%{srcname}
Version:        4.3.1
%define commit 5e626d48c1e57553f54071fd6e7829f22db9c298
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        0.%{scriptsversion}%{?dist}
Summary:        Python access to Moira

Group:          Development/Languages
License:        MIT
URL:            https://github.com/mit-scripts/python-moira
Source0:        https://github.com/mit-scripts/python-moira/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%global _description %{expand:
Moira bindings for Python.}

%description %_description

%package -n python2-%{srcname}
Summary:        %{summary}
BuildRequires:  python2-devel
BuildRequires:  python2-Cython
BuildRequires:  libmoira-devel
BuildRequires:  libmrclient-devel
BuildRequires:  gcc
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname} %_description


%package -n python3-%{srcname}
Summary:        %{summary}
BuildRequires:  python3-devel
BuildRequires:  python3-Cython
BuildRequires:  libmoira-devel
BuildRequires:  libmrclient-devel
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
%{python2_sitearch}/*

%files -n python3-%{srcname}
%license COPYING
%doc README
%{python3_sitearch}/*
/usr/bin/qy


%changelog
* Wed Dec 11 2019 Quentin Smith <quentin@mit.edu> - 4.3.1
- Add support for Python 3

* Sun Oct 13 2013 Alex Dehnert <adehnert@mit.edu> - 4.3.0
- Initial RPM release

