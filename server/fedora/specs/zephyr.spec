Name:           zephyr
Version:        3.0.1
Release:        0.%{scriptsversion}%{?dist}
Summary:        Client programs for the Zephyr real-time messaging system

Group:          Applications/Communications
License:        MIT
URL:            http://zephyr.1ts.org/
Source0:        http://zephyr.1ts.org/export/HEAD/distribution/%{name}-%{version}.tar.gz
Source1:        zhm.init
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  krb5-devel hesiod-devel libss-devel libcom_err-devel readline-devel bison
Requires:       %{name}-libs = %{version}-%{release}
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

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
%setup -q
cp -p %{SOURCE1} .


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

mkdir -p $RPM_BUILD_ROOT%{_initddir}
install -m755 zhm.init \
        $RPM_BUILD_ROOT%{_initddir}/zhm


%post
/sbin/chkconfig --add zhm


%preun
if [ $1 = 0 ] ; then
    /sbin/service zhm stop >/dev/null 2>&1
    /sbin/chkconfig --del zhm
fi


%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service zhm condrestart >/dev/null 2>&1 || :
fi


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
%{_initddir}/zhm


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


%changelog
* Sat Apr 16 2011 Alexander Chernyakhovsky <achernya@mit.edu> 3.0.1-0
- Zephyr 3.0.1

* Sun Sep 19 2010 Anders Kaseorg <andersk@mit.edu> - 3.0-0
- Decrease version below a hypothetical Fedora package.
- Split out -server, -libs, and -devel into subpackages.
- Disable the static library and remove the libtool archive.

* Thu Sep 09 2010 Edward Z. Yang <ezyang@mit.edu> 3.0-1
- Initial packaging release, superseding mit-zephyr.
