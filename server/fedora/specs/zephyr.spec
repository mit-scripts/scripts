Name:           zephyr
Version:        3.1.2
%define commit 54c6b84a81301a1691f9bec10c63c1e36166df9d
%define shortcommit %(c=%{commit}; echo ${c:0:7})
Release:        1.%{scriptsversion}%{?dist}
Summary:        Client programs for the Zephyr real-time messaging system

Group:          Applications/Communications
License:        MIT
URL:            http://zephyr.1ts.org/
Source0:        https://github.com/zephyr-im/zephyr/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
Patch0:         zephyr-zhm-service.patch
Patch1:         zephyr-zhm-pidfile.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  krb5-devel hesiod-devel libss-devel libcom_err-devel readline-devel bison
BuildRequires:  gcc
BuildRequires:  (systemd-rpm-macros or systemd < 240)
Requires:       %{name}-libs = %{version}-%{release}

%description
Zephyr is an institutional/enterprise-scale distributed real-time messaging and
notification system.  Zephyr's design choices seem to imbue it with a specific
culture.  It is impossible to explain what Zephyr is, you must experience it
for yourself.


%package        server
Summary:        Server for the Zephyr real-time messaging system
Group:          System Environment/Daemons

Requires:       %{name}-libs = %{version}-%{release}

%description    server
The %{name}-server package contains the server daemon for the Zephyr
messaging service.  It maintains a location and subscription database
for all the receiving clients, and routes all zephyrgrams to the
intended recipients.


%package        libs
Summary:        Shared libraries for Zephyr real-time messaging system
Group:          System Environment/Libraries

%description    libs
The %{name}-libs package contains shared libraries for applications
that use %{name}.


%package        devel
Summary:        Development files for Zephyr real-time messaging system
Group:          Development/Libraries

Requires:       %{name}-libs = %{version}-%{release}, libcom_err-devel

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%autosetup -n %{name}-%{commit} -p1


%build
# Mitch wants to make an awesome specfile which makes hesiod/krb5 and friends
# all fully configurable.  This configure line will have to do for now.
%configure --with-hesiod --with-krb5 --disable-static
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir}
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -m755 zhm.service \
        $RPM_BUILD_ROOT%{_unitdir}/zhm.service
# Make RPM's Provide: searcher actually search the .so files! A recent
# change in how RPM detects Provides automatically means that only
# files that are executable get searched. Without this hack, all of
# the zephyr client tools are Requires: libzephyr.so.4 which is never
# Provides:, leading to uninstallable RPMS. This can be removed when
# zephyr starts installing the libraries with mode 755 rather than
# 644. (Zephyr #79)
chmod a+x $RPM_BUILD_ROOT%{_libdir}/libzephyr.so.*

%post
%systemd_post zhm.service


%preun
%systemd_preun zhm.service


%postun
%systemd_postun zhm.service

%post           libs -p /sbin/ldconfig

%postun         libs -p /sbin/ldconfig


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README USING
%{_bindir}/*
%{_sbindir}/zhm
%{_sbindir}/zshutdown_notify
%{_mandir}/man1/*
%{_mandir}/man8/zhm.8*
%{_mandir}/man8/zstat.8*
%{_mandir}/man8/zshutdown_notify.8*
%{_datadir}/zephyr
%{_unitdir}/zhm.service


%files          server
%doc OPERATING
%{_sysconfdir}/zephyr
%{_sbindir}/zephyrd
%{_mandir}/man8/zephyrd.8*


%files          libs
%{_libdir}/*.so.*


%files          devel
%{_libdir}/*.so
%{_includedir}/*
%{_libdir}/pkgconfig/zephyr.pc

%changelog
* Wed Jun 26 2019 Quentin Smith <quentin@mit.edu> - 3.1.2-1
- Fix packaging for F30

* Mon May 26 2014 Alexander Chernyakhovsky <achernya@mit.edu> - 3.1.2-0
- Update to Zephyr 3.1.2, fix packaging for F20

* Sat Apr 16 2011 Alexander Chernyakhovsky <achernya@mit.edu> 3.0.1-0
- Zephyr 3.0.1

* Sun Sep 19 2010 Anders Kaseorg <andersk@mit.edu> - 3.0-0
- Decrease version below a hypothetical Fedora package.
- Split out -server, -libs, and -devel into subpackages.
- Disable the static library and remove the libtool archive.

* Thu Sep 09 2010 Edward Z. Yang <ezyang@mit.edu> 3.0-1
- Initial packaging release, superseding mit-zephyr.
