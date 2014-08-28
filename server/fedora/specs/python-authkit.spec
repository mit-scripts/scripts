# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:		python-authkit
Version:	0.4.5
Release:	2%{?dist}
Summary:	An authentication and authorization toolkit for WSGI applications and frameworks

License:	MIT
URL:		https://pypi.python.org/pypi/AuthKit/0.4.5
Source0:	https://pypi.python.org/packages/source/A/AuthKit/AuthKit-0.4.5.tar.gz

BuildArch:	noarch

BuildRequires:	python-setuptools
BuildRequires:	python2-devel

Requires:	python-beaker
Requires:	python-decorator
Requires:	python-nose
Requires:	python-openid
Requires:	python-paste
Requires:	python-paste-deploy
Requires:	python-paste-script
Requires:	python-webob

Patch0:		python-authkit.patch

%description
* Built for WSGI applications and middleware
* Sophisticated and extensible permissions system
* Built in support for HTTP basic, HTTP digest, form, cookie and
  OpenID authentication methods plus others
* Easily define users, passwords and roles
* Designed to be totally extensible so you can use the components to
  integrate with a database, LDAP connection or your own custom system
* Plays nicely with the Pylons web framework


%prep
%setup -q -n AuthKit-%{version}
%patch0 -p1


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%files
%doc
# For noarch packages: sitelib
%{python_sitelib}/*


%changelog
* Thu Aug 28 2014 Alex Chernyakhovsky <achernya@mit.edu> - 0.4.5-2
- Correct ElementTree import.

* Thu Aug 28 2014 Alex Chernyakhovsky <achernya@mit.edu> - 0.4.5-1
- Initial packaging.
