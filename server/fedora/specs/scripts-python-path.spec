Summary: scripts.mit.edu python path configuration
Group: Development/Languages
Name: scripts-python-path
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz 
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root

%description 

scripts.mit.edu python path configuration
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{python_sitelib}
install -m 644 00scripts-home.pth $RPM_BUILD_ROOT%{python_sitelib}

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
%dir %{python_sitelib}
%{python_sitelib}/00scripts-home.pth

%changelog
* Thu Jul  9 2009  Geoffrey Thomas <geofft@mit.edu>
- Update to Python 2.6
* Tue Jan 27 2009  Quentin Smith <quentin@mit.edu>
- initial release
