Summary: rpm packaging of libmoira
Group: Applications/System
Name: moira
Version: 0.%{scriptsversion}
Release: 0
Vendor: The scripts.mit.edu Team (scripts@mit.edu)
URL: http://scripts.mit.edu
License: GPL
Source: %{name}.tar.gz
Source1: debian/debathena-moira-update-server.init
BuildRoot: %{_tmppath}/%(%{__id_u} -n)-%{name}-%{version}-root
#TODO: might really need mit-zephyr-devel, something for autotools-dev
BuildRequires: readline-devel, patch, e2fsprogs-devel, mit-zephyr, ncurses-devel, krb5-devel, hesiod-devel
patch0: debian/patches/install-headers

%description
rpm packaging of libmoira

Source package for the moira library and clients.  Clone of debathena-moira.
See http://scripts.mit.edu/wiki for more information.

%prep
%setup -q -n %{name}
cp -p /home/scripts-build/test/trunk/server/fedora/specs/mybuild/moira-update-server.init %{SOURCE1}
%patch0 -p1

%build
# Hack: Add /usr/include/et to put com_err.h on the C include path.
# Can remove this once the maintainer of the relevant package symlinks
# com_err.h in /usr/include.
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
install -m 755 %{SOURCE1} %{buildroot}/%{_initddir}/moira-update-server
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

%changelog
* Fri Dec 26 2009  Greg Brockman <gdb@mit.edu>
- prerelease

# moira-clients
%package moira-clients
Summary: Clients for the Moira database
Group: Applications/System
%description moira-clients
Clients for the Moira database

Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains clients such as moira, stella, blanche, etc.

%files moira-clients
%{_bindir}/addusr
%{_bindir}/blanche
%{_bindir}/chfn.moira
%{_bindir}/chpobox
%{_bindir}/chsh.moira
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
%doc %{_mandir}/man1/*
%doc %{_mandir}/man8/mrtest.8.gz


# moira-update-server
%package moira-update-server
Summary: Athena update_server
Group: Applications/System
Requires(post): chkconfig
Requires(preun): chkconfig
%description moira-update-server
Athena update_server

Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains the update_server daemon, which is used for
servers that automatically receive information dumps from moira.

%files moira-update-server
%defattr(-,root,root)
%doc %{_mandir}/man8/update_server.8.gz
%config(noreplace) %{_sysconfdir}/athena/moira.conf
%defattr(755,root,root)
%{_sbindir}/update_server
%{_initddir}/moira-update-server

%post moira-update-server
/sbin/chkconfig --add moira-update-server

%preun moira-update-server
if [ $1 = 0 ] ; then
    /sbin/service moira-update-server stop >/dev/null 2>&1
    /sbin/chkconfig --del moira-update-server
fi

# libmoira0
%package libmoira0
Summary: The Moira library
Group: System Environment/Libraries
%description libmoira0
The Moira library

Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains the shared Moira library.

%files libmoira0
%{_libdir}/libmoira.so.*

# libmoira-dev
%package libmoira-dev
Summary: Development files for Moira library
Group: Development/Libraries
Provides: libmoira-dev
Requires: libmoira0
%description libmoira-dev
Development files for Moira library

Moira is the Athena Service Management system.  It serves as the 
central repository for information about users, groups hosts, print 
queues, and several other aspects of the Athena environment.

This package contains headers and static libraries for development.

%files libmoira-dev
%defattr(-,root,root)
%{_includedir}/*
%doc %{_mandir}/man3/*
%{_libdir}/libmoira.so
%{_libdir}/libmoira.la
%{_libdir}/libmoira.a
