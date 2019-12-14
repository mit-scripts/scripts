%global srcname afs
Name:           python-%{srcname}
Version:        0.1.2
%define commit 035a1a7b0ecb118e73c1cd7e46f6ba2e9efa5298
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        0.%{scriptsversion}%{?dist}
Summary:        Python access to AFS library

Group:          Development/Languages
License:        GPL
URL:            https://github.com/mit-scripts/pyafs
Source0:        https://github.com/mit-scripts/pyafs/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel, python-setuptools, Cython, openafs-devel, openafs-authlibs-devel, krb5-devel

%global _description %{expand:
Get at AFS from Python.}

%description %_description

%package -n python2-%{srcname}
Summary:        %{summary}
BuildRequires:  python2-devel
BuildRequires:  python2-Cython
BuildRequires:  openafs-devel
BuildRequires:  openafs-authlibs-devel
BuildRequires:  krb5-devel
BuildRequires:  gcc
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname} %_description


%package -n python3-%{srcname}
Summary:        %{summary}
BuildRequires:  python3-devel
BuildRequires:  python3-Cython
BuildRequires:  openafs-devel
BuildRequires:  openafs-authlibs-devel
BuildRequires:  krb5-devel
BuildRequires:  gcc
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname} %_description


%prep
%autosetup -n pyafs-%{commit}


%build
%py2_build
%py3_build

%install
%py2_install
%py3_install
 
%files -n python2-%{srcname}
%doc README
%{python2_sitearch}/afs/*
%{python2_sitearch}/PyAFS-*

%files -n python3-%{srcname}
%doc README
%{python3_sitearch}/afs/*
%{python3_sitearch}/PyAFS-*


%changelog
* Fri Dec 13 2019 Quentin Smith <quentin@mit.edu> - 0.1.2
- Add support for Python 3

* Thu Dec 15 2011 Alex Dehnert <adehnert@mit.edu> - 0.1.1
- Initial RPM release

