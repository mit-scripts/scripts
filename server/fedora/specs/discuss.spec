# Make sure to update this to coincide with the most recent debathena-discuss
# release from http://debathena.mit.edu/apt/pool/debathena/d/debathena-discuss/
%define upstreamversion 10.0.17
Name:		discuss
Version:	%{upstreamversion}
Release:	1.%{scriptsversion}%{?dist}
Vendor:		The scripts.mit.edu Team (scripts@mit.edu)
Summary:	A conferencing and mail archiving system
Group:		Applications/Archiving
License:	MIT
URL:		http://scripts.mit.edu/
Source0:	debathena-%{name}_%{upstreamversion}.orig.tar.gz
Source1:	discuss.xinetd
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:	gcc
BuildRequires:	athena-aclocal, byacc, libcom_err-devel, libss-devel, krb5-devel, zephyr-devel, readline-devel, less
Requires:	less

%description
Discuss is a user-interface front end to a networked conferencing system.
This is a clone of Debathena's debathena-discuss package.

%prep
%setup -q -n %{name}-%{upstreamversion}

%build
autoreconf -fi
# automake doesn't like that there's no Makefile.am, but we're only
# using it to copy in install-sh and config.{sub|guess}, so we don't
# want the error return code to cause rpmbuild to bomb out.
automake --add-missing --foreign || :
%configure --without-krb4 --with-krb5 --with-zephyr --with-pager=/usr/bin/less
#make %{?_smp_mflags}
make

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# Unfortunately, discuss's build system doesn't presently support
# building shared libraries, so we won't be installing any of the
# dev stuff at all just yet.
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/xinetd.d/%{name}
mkdir -p %{buildroot}%{_localstatedir}/spool/discuss

%clean
rm -rf %{buildroot}

%files
%defattr(755,root,root)
%{_bindir}/crmtgs
%{_bindir}/discuss
%{_bindir}/dsc_setup
%{_bindir}/dsgrep
%{_bindir}/dsmail
%{_bindir}/dspipe
%{_bindir}/mkds
%{_bindir}/rmds
%{_libexecdir}/edsc
%defattr(-,root,root,-)
/usr/share/discuss
%doc %{_mandir}/man1/*.1.gz
%doc %{_mandir}/man8/*.8.gz

%post
if ! grep -q '^discuss[[:space:]]' %{_sysconfdir}/services; then
    cat <<EOF >>%{_sysconfdir}/services
discuss         2100/tcp                # Networked conferencing
EOF
fi

%package emacs
Summary: Emacs interface to discuss
Group: Applications/Archiving
Requires: %{name}%{?_isa} = %{version}-%{release}, emacs
%description emacs
Discuss is a user-interface front end to a networked conferencing system.
This package contains an Emacs interface to discuss.

%files emacs
%defattr(-,root,root,-)
%{_datadir}/emacs/site-lisp/*.el

%package server
Summary: A conferencing and mail archiving system
Group: Applications/Archiving
Requires(pre): shadow-utils
Requires: %{name}%{?_isa} = %{version}-%{release}, xinetd
%description server
A conferencing and mail archiving system.
This package contains the discuss server.

%files server
%defattr(755,root,root)
%{_bindir}/create_mtg_dir
%{_sbindir}/discussd
%attr(4755,discuss,discuss) %{_sbindir}/disserve
%attr(755,discuss,discuss) %{_localstatedir}/spool/discuss
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/xinetd.d/%{name}
%{_libexecdir}/disdebug
%{_libexecdir}/expunge
%{_libexecdir}/recover

%pre server
getent group discuss >/dev/null || groupadd -r discuss
getent passwd discuss >/dev/null || \
    useradd -r -M -g discuss -d /var/spool/discuss -s /sbin/nologin \
    -c "Discuss server" discuss
exit 0

%changelog
* Mon May 26 2014 Alexander Chernyakhovsky <achernya@mit.edu> - 10.0.17-1
- Update to discuss 10.0.17

* Tue Mar 19 2013 Alexander Chernyakhovsky <achernya@mit.edu> - 10.0.15-1
- Update to discuss 10.0.15

* Sun May 29 2011 Mitchell Berger <mitchb@mit.edu> - 10.0.13-1
- Initial packaging of Discuss on Fedora

