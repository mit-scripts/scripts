%global srcname authkit
Name:		python-%{srcname}
Version:	0.4.5
Release:	3%{?dist}
Summary:	An authentication and authorization toolkit for WSGI applications and frameworks

License:	MIT
URL:		https://pypi.python.org/pypi/AuthKit/0.4.5
Source0:	https://pypi.python.org/packages/source/A/AuthKit/AuthKit-0.4.5.tar.gz

BuildArch:	noarch

BuildRequires:	python-setuptools
BuildRequires:	python2-devel

Patch0:		python-authkit.patch

%global _description %{expand:
* Built for WSGI applications and middleware
* Sophisticated and extensible permissions system
* Built in support for HTTP basic, HTTP digest, form, cookie and
  OpenID authentication methods plus others
* Easily define users, passwords and roles
* Designed to be totally extensible so you can use the components to
  integrate with a database, LDAP connection or your own custom system
* Plays nicely with the Pylons web framework}

%description %_description

%package -n python2-%{srcname}
Summary:        %{summary}
BuildRequires:  python2-devel
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname} %_description


%prep
%setup -q -n AuthKit-%{version}
%patch0 -p1


%build
%py2_build


%install
%py2_install

 
%files -n python2-%{srcname}
%license LICENSE.txt
%doc README.txt
# For noarch packages: sitelib
%{python2_sitelib}/authkit/*
%{python2_sitelib}/AuthKit-*


%changelog
* Thu Aug 28 2014 Alex Chernyakhovsky <achernya@mit.edu> - 0.4.5-2
- Correct ElementTree import.

* Thu Aug 28 2014 Alex Chernyakhovsky <achernya@mit.edu> - 0.4.5-1
- Initial packaging.
