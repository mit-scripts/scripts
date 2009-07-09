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

%install
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT
install -D 00scripts-home.pth $RPM_BUILD_ROOT/usr/lib/python2.6/site-packages

%clean
[ $RPM_BUILD_ROOT != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root)
/usr/lib/python2.6/site-packages/00scripts-home.pth

%changelog
* Thu Jul  9 2009  Geoffrey Thomas <geofft@mit.edu>
- Update to Python 2.6
* Tue Jan 27 2009  Quentin Smith <quentin@mit.edu>
- initial release
