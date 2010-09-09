Name:           zephyr
Version:        3.0
Release:        1.%{scriptsversion}%{?dist}
Summary:        Zephyr allows users to send messages to other users or to groups of users.

Group:          Applications/Communications
License:        MIT
URL:            http://zephyr.1ts.org/
Source0:        http://zephyr.1ts.org/export/HEAD/distribution/%{name}-%{version}.tar.gz
Source1:        zhm.init
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  krb5-devel hesiod-devel libss-devel readline-devel bison
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

%description
Zephyr is an institutional/enterprise-scale distributed real-time messaging and
notification system.  Zephyr's design choices seem to imbue it with a specific
culture.  It is impossible to explain what Zephyr is, you must experience it
for yourself.


%prep
%setup -q


%build
# Mitch wants to make an awesome specfile which makes hesiod/krb5 and friends
# all fully configurable.  This configure line will have to do for now.
%configure --with-hesiod=%{_usr} --with-krb5=%{_usr}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir}

mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
install -m755 $RPM_SOURCE_DIR/zhm.init \
        $RPM_BUILD_ROOT/etc/rc.d/init.d/zhm


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


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README NOTES OPERATING USING
%{_bindir}/*
%{_sbindir}/*
%{_includedir}/%{name}/
%{_libdir}/*
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_datadir}/%{name}/
%{_sysconfdir}/%{name}/
%{_sysconfdir}/rc.d/init.d/zhm


%changelog
* Thu Sep 09 2010 Edward Z. Yang <ezyang@mit.edu> 3.0-1
- Initial packaging release, superseding mit-zephyr.
