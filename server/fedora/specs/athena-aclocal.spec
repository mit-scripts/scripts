# Make sure to update this to coincide with the most recent debathena-aclocal
# release from http://debathena.mit.edu/apt/pool/debathena/d/debathena-aclocal/
%define upstreamversion 1.1.2
Name:		athena-aclocal
Version:	%{upstreamversion}
Release:	1.%{scriptsversion}%{?dist}
Summary:	Common autoconf macros for Athena software
Vendor:		The scripts.mit.edu Team (scripts@mit.edu)
Group:		Development/Tools
License:	MIT
URL:		http://scripts.mit.edu/
Source:		deb%{name}_%{upstreamversion}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Requires:	automake

%description
This package contains autoconf macros used in the building of multiple
pieces of Athena software.  It is a clone of Debathena's debathena-aclocal.

%prep
%setup -q -n deb%{name}-%{upstreamversion}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_datadir}/aclocal
cp aclocal/* %{buildroot}%{_datadir}/aclocal

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_datadir}/aclocal/*.m4

%changelog
* Sun May 29 2011 Mitchell Berger <mitchb@mit.edu> - 1.1.2-1
- Initial packaging of Athena aclocal macros on Fedora

