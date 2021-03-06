# Make sure to update these to coincide with the most recent debathena-moira
# release from http://debathena.mit.edu/apt/pool/debathena/d/debathena-moira/
%define upstreamversion 4.0.0
%define snapshotversion svn20100405
Summary: moira libraries, clients, and friends
Group: Applications/System
Name: moira
Version: %{upstreamversion}
Release: 6.%{scriptsversion}.%{snapshotversion}
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: MIT
Source: debathena-%{name}_%{upstreamversion}+%{snapshotversion}.orig.tar.gz
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
#TODO: might really need mit-zephyr-devel, something for autotools-dev
BuildRequires: readline-devel, e2fsprogs-devel, ncurses-devel, krb5-devel, hesiod-devel
Patch1: moira-update-server.rc.patch
Patch2: moira-fix-manpage-paths.patch

%description
The moira library and clients.  Clone of debathena-moira.
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n debathena-%{name}-%{upstreamversion}+%{snapshotversion}
%patch1
%patch2 -p1

%build
# Hack: Add /usr/include/et to put com_err.h on the C include path.
# Can remove this once the maintainer of the relevant package symlinks
# com_err.h in /usr/include.
# (See https://bugzilla.redhat.com/show_bug.cgi?id=550889)
# TODO: --with-zephyr is currently borked
%configure --without-krb4 --with-krb5 --with-hesiod --without-zephyr --without-oracle --without-afs --disable-rpath --with-com_err=/usr CFLAGS='-I /usr/include/et'
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
mv %{buildroot}/%{_bindir}/chfn %{buildroot}/%{_bindir}/chfn.moira
mv %{buildroot}/%{_bindir}/chsh %{buildroot}/%{_bindir}/chsh.moira
mv %{buildroot}/%{_mandir}/man1/chsh.1 \
   %{buildroot}/%{_mandir}/man1/chsh.moira.1
mv %{buildroot}/%{_mandir}/man1/chfn.1 \
   %{buildroot}/%{_mandir}/man1/chfn.moira.1
install -m 755 -d %{buildroot}/%{_initddir}
install -m 755 moira-update-server.init %{buildroot}/%{_initddir}/moira-update-server
# Hack: These man files are installed but no package uses them
rm %{buildroot}/%{_mandir}/man8/dcm.8
rm %{buildroot}/%{_mandir}/man8/moirad.8
rm %{buildroot}/%{_mandir}/man8/reg_svr.8
rm %{buildroot}/%{_mandir}/man8/setquota.8
rm %{buildroot}/%{_mandir}/man8/startdcm.8
rm %{buildroot}/%{_mandir}/man8/startmoira.8
rm %{buildroot}/%{_mandir}/man8/startreg.8

%clean
rm -rf %{buildroot}

# clients
%package clients
Summary: Clients for the Moira database
Group: Applications/System
# Might need mit-zephyr-devel
# Requires: mit-zephyr
%description clients
Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains clients such as moira, stella, blanche, etc.

%files clients
%defattr(755,root,root)
%{_bindir}/addusr
%{_bindir}/blanche
%{_bindir}/chfn.moira
%{_bindir}/chpobox
%{_bindir}/chsh.moira
%{_bindir}/eunice
%{_bindir}/mitch
%{_bindir}/namespace
%{_bindir}/moira
%{_bindir}/mrcheck
%{_bindir}/mrtest
%{_bindir}/stanley
%{_bindir}/stella
%{_bindir}/mailmaint
%{_bindir}/listmaint
%{_bindir}/dcmmaint
%{_bindir}/usermaint
%{_bindir}/update_test
%defattr(-,root,root)
%doc %{_mandir}/man1/*
%doc %{_mandir}/man8/mrtest.8.gz


# update-server
%package update-server
Summary: Athena update_server
Group: Applications/System
# Might need mit-zephyr-devel
# Requires: mit-zephyr
Requires(post): chkconfig
Requires(preun): chkconfig
%description update-server
Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains the update_server daemon, which is used for
servers that automatically receive information dumps from moira.

%files update-server
%defattr(-,root,root)
%doc %{_mandir}/man8/update_server.8.gz
%config(noreplace) %{_sysconfdir}/moira.conf
%defattr(755,root,root)
%{_sbindir}/update_server
%{_initddir}/moira-update-server

%post update-server
/sbin/chkconfig --add moira-update-server
%{_initddir}/moira-update-server condrestart

%preun update-server
if [ $1 = 0 ] ; then
    /sbin/service moira-update-server stop >/dev/null 2>&1
    /sbin/chkconfig --del moira-update-server
fi

# libmoira0
%package -n libmoira0
Summary: The Moira library
Group: System Environment/Libraries
%description -n libmoira0
Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains the shared Moira library.

%post -n libmoira0 -p /sbin/ldconfig
%postun -n libmoira0 -p /sbin/ldconfig

%files -n libmoira0
%defattr(-,root,root)
%{_libdir}/libmoira.so.*

# libmoira-devel
%package -n libmoira-devel
Summary: Development files for Moira library
Group: Development/Libraries
# Might need mit-zephyr-devel
# Requires: mit-zephyr
Requires: libmoira0 = %{version}-%{release}, e2fsprogs-devel, krb5-devel, hesiod-devel
%description -n libmoira-devel
Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains headers and static libraries for development.

%post -n libmoira-devel -p /sbin/ldconfig
%postun -n libmoira-devel -p /sbin/ldconfig

%files -n libmoira-devel
%defattr(-,root,root)
%{_includedir}/moira
%exclude %{_includedir}/moira/mrclient.h
%doc %{_mandir}/man3/*
%{_libdir}/libmoira.so
%{_libdir}/libmoira.la
%{_libdir}/libmoira.a

# libmrclient0
%package -n libmrclient0
Summary: The Moira client library
Group: System Environment/Libraries
%description -n libmrclient0
Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains the shared Moira client library.

%post -n libmrclient0 -p /sbin/ldconfig
%postun -n libmrclient0 -p /sbin/ldconfig

%files -n libmrclient0
%defattr(-,root,root)
%{_libdir}/libmrclient.so.*

# libmrclient-devel
%package -n libmrclient-devel
Summary: Development files for Moira client library
Group: Development/Libraries
Requires: libmrclient0 = %{version}-%{release}, libmoira-devel = %{version}-%{release}
%description -n libmrclient-devel
Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains headers and static libraries for development.

%post -n libmrclient-devel -p /sbin/ldconfig
%postun -n libmrclient-devel -p /sbin/ldconfig

%files -n libmrclient-devel
%defattr(-,root,root)
%{_includedir}/moira/mrclient.h
%{_libdir}/libmrclient.so
%{_libdir}/libmrclient.la
%{_libdir}/libmrclient.a

%changelog
* Thu Apr 08 2010 Mitchell Berger <mitchb@mit.edu> - 4.0.0-6.1534.svn20100405
- Update to new original upstream version (svn snapshot)

* Thu Feb 25 2010 Mitchell Berger <mitchb@mit.edu> - 4.0.0-5.1490.svn20100225
- Update to new original upstream version (svn snapshot)

* Thu Feb 25 2010 Mitchell Berger <mitchb@mit.edu> - 4.0.0-4.1489M.svn20100223
- Update to new original upstream version (svn snapshot)
- Drop install-headers patch which was incorporated upstream (from Debathena)

* Tue Jan 05 2010 Mitchell Berger <mitchb@mit.edu> - 4.0.0-3.1405M.svn20100104
- Update to new original upstream version (svn snapshot)
- Build and install libmrclient as a shared library (from Debathena)

* Mon Dec 28 2009 Mitchell Berger <mitchb@mit.edu> - 4.0.0-2.1402.cvs20091228
- Update to new upstream version, including eunice printer client

* Sat Dec 26 2009 Greg Brockman <gdb@mit.edu> - 4.0.0-2.1380.cvs20091116
- Initial packaging of Moira on Fedora
