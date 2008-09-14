%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:		python-routefs
Version:	0.0.1
Release:	1%{?dist}
Summary:	A FUSE API wrapper based on URL routing

Group:		Development/Languages
License:	MIT
URL:		http://ebroder.net/code/python-routefs.git
Source0:	python-routefs.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	python-devel
BuildRequires:	python-routes >= 1.7
BuildRequires:	fuse-python >= 0.2
Requires:	python-routes >= 1.7
Requires:	fuse-python >= 0.2

%description

RouteFS is a base class for developing read-only FUSE filesystems that
lets you focus on the directory tree instead of the system calls.

RouteFS uses the Routes library developed for Pylons. URLs were
inspired by filesystems, and now you can have filesystems inspired by
URLs.


%prep
%setup -q -n %{name}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{python_sitelib}/*


%changelog
* Sun Sep 14 2008 Anders Kaseorg <andersk@mit.edu> - 0.0.1
- Initial RPM release.
