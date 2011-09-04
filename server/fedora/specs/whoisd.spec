Summary:   whoisd for <scripts.mit.edu> (virtualhost aware)
Group:     Applications/System
Name:      whoisd
Version:   0.%{scriptsversion}
Release:   1
Vendor:    The scripts.mit.edu Team (scripts@mit.edu)
URL:       http://scripts.mit.edu
License:   GPL
Source0:   %{name}.tar.gz

%define debug_package %{nil}

Requires:      python-twisted-core
BuildRequires: systemd-units

Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires(post):   systemd-sysv

%description


%prep
%setup -q -n %{name}

%build
./configure

%install
make install DESTDIR=$RPM_BUILD_ROOT exec_prefix=/usr/local

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl enable scripts-whoisd.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ]; then
    /bin/systemctl --no-reload disable scripts-whoisd.service >/dev/null 2>&1 || :
    /bin/systemctl stop scripts-whoisd.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
    /bin/systemctl try-restart scripts-whoisd.service >/dev/null 2>&1 || :
fi

%files
%defattr(0644,root,root,-)
/usr/local/libexec/whoisd.tac
%defattr(0644,root,root)
/lib/systemd/system/scripts-whoisd.service

%changelog
* Thu Aug 25 2011 Alexander Chernyakhovsky <achernya@mit.edu> 0-1
- package systemd service file

* Tue Jun 03 2008 Joe Presbrey <presbrey@mit.edu> 0.00
- prerelease
