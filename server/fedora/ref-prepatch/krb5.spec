%if %{?WITH_SELINUX:0}%{!?WITH_SELINUX:1}
%define WITH_SELINUX 0
%endif

%define krb5prefix %{_prefix}/kerberos

# FIXME: is it upstream's intention that the new autoconf macro be installed?
%define install_macro 0

Summary: The Kerberos network authentication system.
Name: krb5
Version: 1.5
Release: 7
# Maybe we should explode from the now-available-to-everybody tarball instead?
# http://web.mit.edu/kerberos/dist/krb5/1.5/krb5-1.5-signed.tar
Source0: krb5-%{version}.tar.gz
Source1: krb5-%{version}.tar.gz.asc
Source2: kpropd.init
Source3: krb524d.init
Source4: kadmind.init
Source5: krb5kdc.init
Source6: krb5.conf
Source7: krb5.sh
Source8: krb5.csh
Source9: kdcrotate
Source10: kdc.conf
Source11: kadm5.acl
Source12: krsh
Source13: krlogin
Source14: eklogin.xinetd
Source15: klogin.xinetd
Source16: kshell.xinetd
Source17: krb5-telnet.xinetd
Source18: gssftp.xinetd
Source19: krb5kdc.sysconfig
Source20: kadmin.sysconfig
Source21: krb524.sysconfig
Source22: ekrb5-telnet.xinetd

Patch2: krb5-1.3-manpage-paths.patch
Patch3: krb5-1.3-netkit-rsh.patch
Patch4: krb5-1.3-rlogind-environ.patch
Patch5: krb5-1.3-ksu-access.patch
Patch6: krb5-1.5-ksu-path.patch
Patch9: krb5-1.5-brokenrev.patch
Patch11: krb5-1.2.1-passive.patch
Patch12: krb5-1.4-ktany.patch
Patch13: krb5-1.3-large-file.patch
Patch14: krb5-1.3-ftp-glob.patch
Patch15: krb5-1.3-check.patch
Patch16: krb5-1.5-no-rpath.patch
Patch18: krb5-1.2.7-reject-bad-transited.patch
Patch21: krb5-selinux.patch
Patch23: krb5-1.3.1-dns.patch
Patch25: krb5-1.4-null.patch
Patch26: krb5-1.3.2-efence.patch
Patch27: krb5-1.3.3-rcp-sendlarge.patch
Patch29: krb5-1.3.5-kprop-mktemp.patch
Patch30: krb5-1.3.4-send-pr-tempfile.patch
Patch32: krb5-1.4-ncurses.patch
Patch33: krb5-1.5-io.patch
Patch35: krb5-1.5-fclose.patch
Patch36: krb5-1.3.3-rcp-markus.patch
Patch39: krb5-1.4.1-api.patch
Patch40: krb5-1.4.1-telnet-environ.patch
Patch41: krb5-1.2.7-login-lpass.patch
Patch44: krb5-1.4.3-enospc.patch
Patch45: krb5-1.5-gssinit.patch
Patch46: http://web.mit.edu/kerberos/advisories/2006-001-patch_1.5.txt

License: MIT, freely distributable.
URL: http://web.mit.edu/kerberos/www/
Group: System Environment/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Prereq: grep, info, sh-utils, /sbin/install-info
BuildPrereq: autoconf, bison, e2fsprogs-devel >= 1.35, flex
BuildPrereq: gzip, ncurses-devel, rsh, texinfo, tar

Patch1000: krb5-kuserok-scripts.patch

%description
Kerberos V5 is a trusted-third-party network authentication system,
which can improve your network's security by eliminating the insecure
practice of cleartext passwords.

%package devel
Summary: Development files needed to compile Kerberos 5 programs.
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}, e2fsprogs-devel

%description devel
Kerberos is a network authentication system. The krb5-devel package
contains the header files and libraries needed for compiling Kerberos
5 programs. If you want to develop Kerberos-aware programs, you need
to install this package.

%package libs
Summary: The shared libraries used by Kerberos 5.
Group: System Environment/Libraries
Prereq: grep, /sbin/ldconfig, sh-utils
Obsoletes: krb5-configs

%description libs
Kerberos is a network authentication system. The krb5-libs package
contains the shared libraries needed by Kerberos 5. If you are using
Kerberos, you need to install this package.

%package server
Group: System Environment/Daemons
Summary: The server programs for Kerberos 5.
Requires: %{name}-libs = %{version}-%{release}
Prereq: grep, /sbin/install-info, /bin/sh, sh-utils, /sbin/chkconfig

%description server
Kerberos is a network authentication system. The krb5-server package
contains the programs that must be installed on a Kerberos 5 server.
If you are installing a Kerberos 5 server, you need to install this
package (in other words, most people should NOT install this
package).

%package workstation
Summary: Kerberos 5 programs for use on workstations.
Group: System Environment/Base
Requires: %{name}-libs = %{version}-%{release}
Prereq: grep, /sbin/install-info, /bin/sh, sh-utils
# mktemp is used by krb5-send-pr
Requires: mktemp

%description workstation
Kerberos is a network authentication system. The krb5-workstation
package contains the basic Kerberos programs (kinit, klist, kdestroy,
kpasswd) as well as kerberized versions of Telnet and FTP. If your
network uses Kerberos, this package should be installed on every
workstation.

%changelog
* Wed Sep  6 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-7
- set SS_LIB at configure-time so that libss-using apps get working readline
  support (#197044)

* Fri Aug 18 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-6
- switch to the updated patch for MITKRB-SA-2006-001

* Tue Aug  8 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-5
- apply patch to address MITKRB-SA-2006-001 (CVE-2006-3084)

* Mon Aug  7 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-4
- ensure that the gssapi library's been initialized before walking the
  internal mechanism list in gss_release_oid(), needed if called from
  gss_release_name() right after a gss_import_name() (#198092)

* Tue Jul 25 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-3
- rebuild

* Tue Jul 25 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-2
- pull up latest revision of patch to reduce lockups in rsh/rshd

* Mon Jul 17 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.5-1.2
- rebuild

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.5-1.1
- rebuild

* Thu Jul  6 2006 Nalin Dahyabhai <nalin@redhat.com> 1.5-1
- build

* Wed Jul  5 2006 Nalin Dahyabhai <nalin@redhat.com> 1.5-0
- update to 1.5

* Fri Jun 23 2006 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-9
- mark profile.d config files noreplace (Laurent Rineau, #196447)

* Thu Jun  8 2006 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-8
- add buildprereq for autoconf

* Mon May 22 2006 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-7
- further munge krb5-config so that 'libdir=/usr/lib' is given even on 64-bit
  architectures, to avoid multilib conflicts; other changes will conspire to
  strip out the -L flag which uses this, so it should be harmless (#192692)

* Fri Apr 28 2006 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-6
- adjust the patch which removes the use of rpath to also produce a
  krb5-config which is okay in multilib environments (#190118)
- make the name-of-the-tempfile comment which compile_et adds to error code
  headers always list the same file to avoid conflicts on multilib installations
- strip SIZEOF_LONG out of krb5.h so that it doesn't conflict on multilib boxes
- strip GSS_SIZEOF_LONG out of gssapi.h so that it doesn't conflict on mulitlib
  boxes

* Fri Apr 14 2006 Stepan Kasal <skasal@redhat.com> 1.4.3-5
- Fix formatting typo in kinit.1 (krb5-kinit-man-typo.patch)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> 1.4.3-4.1
- bump again for double-long bug on ppc(64)

* Mon Feb  6 2006 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-4
- give a little bit more information to the user when kinit gets the catch-all
  I/O error (#180175)

* Thu Jan 19 2006 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-3
- rebuild properly when pthread_mutexattr_setrobust_np() is defined but not
  declared, such as with recent glibc when _GNU_SOURCE isn't being used

* Thu Jan 19 2006 Matthias Clasen <mclasen@redhat.com> 1.4.3-2
- Use full paths in krb5.sh to avoid path lookups

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  1 2005 Nalin Dahyabhai <nalin@redhat.com>
- login: don't truncate passwords before passing them into crypt(), in
  case they're significant (#149476)

* Thu Nov 17 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-1
- update to 1.4.3
- make ksu setuid again (#137934, others)

* Tue Sep 13 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.2-4
- mark %%{krb5prefix}/man so that files which are packaged within it are
  flagged as %%doc (#168163)

* Tue Sep  6 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.2-3
- add an xinetd configuration file for encryption-only telnetd, parallelling
  the kshell/ekshell pair (#167535)

* Wed Aug 31 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.2-2
- change the default configured encryption type for KDC databases to the
  compiled-in default of des3-hmac-sha1 (#57847)

* Thu Aug 11 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.2-1
- update to 1.4.2, incorporating the fixes for MIT-KRB5-SA-2005-002 and
  MIT-KRB5-SA-2005-003

* Wed Jun 29 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.1-6
- rebuild

* Wed Jun 29 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.1-5
- fix telnet client environment variable disclosure the same way NetKit's
  telnet client did (CAN-2005-0488) (#159305)
- keep apps which call krb5_principal_compare() or krb5_realm_compare() with
  malformed or NULL principal structures from crashing outright (Thomas Biege)
  (#161475)

* Tue Jun 28 2005 Nalin Dahyabhai <nalin@redhat.com>
- apply fixes from draft of MIT-KRB5-SA-2005-002 (CAN-2005-1174,CAN-2005-1175)
  (#157104)
- apply fixes from draft of MIT-KRB5-SA-2005-003 (CAN-2005-1689) (#159755)

* Fri Jun 24 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.1-4
- fix double-close in keytab handling
- add port of fixes for CAN-2004-0175 to krb5-aware rcp (#151612)

* Fri May 13 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.1-3
- prevent spurious EBADF in krshd when stdin is closed by the client while
  the command is running (#151111)

* Fri May 13 2005 Martin Stransky <stransky@redhat.com> 1.4.1-2
- add deadlock patch, removed old patch

* Fri May  6 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4.1-1
- update to 1.4.1, incorporating fixes for CAN-2005-0468 and CAN-2005-0469
- when starting the KDC or kadmind, if KRB5REALM is set via the /etc/sysconfig
  file for the service, pass it as an argument for the -r flag

* Wed Mar 23 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4-3
- drop krshd patch for now

* Thu Mar 17 2005 Nalin Dahyabhai <nalin@redhat.com>
- add draft fix from Tom Yu for slc_add_reply() buffer overflow (CAN-2005-0469)
- add draft fix from Tom Yu for env_opt_add() buffer overflow (CAN-2005-0468)

* Wed Mar 16 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4-2
- don't include <term.h> into the telnet client when we're not using curses

* Thu Feb 24 2005 Nalin Dahyabhai <nalin@redhat.com> 1.4-1
- update to 1.4
  - v1.4 kadmin client requires a v1.4 kadmind on the server, or use the "-O"
    flag to specify that it should communicate with the server using the older
    protocol
  - new libkrb5support library
  - v5passwdd and kadmind4 are gone
  - versioned symbols
- pick up $KRB5KDC_ARGS from /etc/sysconfig/krb5kdc, if it exists, and pass
  it on to krb5kdc
- pick up $KADMIND_ARGS from /etc/sysconfig/kadmin, if it exists, and pass
  it on to kadmind
- pick up $KRB524D_ARGS from /etc/sysconfig/krb524, if it exists, and pass
  it on to krb524d *instead of* "-m"
- set "forwardable" in [libdefaults] in the default krb5.conf to match the
  default setting which we supply for pam_krb5
- set a default of 24h for "ticket_lifetime" in [libdefaults], reflecting the
  compiled-in default

* Mon Dec 20 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.6-3
- rebuild

* Mon Dec 20 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.6-2
- rebuild

* Mon Dec 20 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.6-1
- update to 1.3.6, which includes the previous fix

* Mon Dec 20 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.5-8
- apply fix from Tom Yu for MITKRB5-SA-2004-004 (CAN-2004-1189)

* Fri Dec 17 2004 Martin Stransky <stransky@redhat.com> 1.3.5-7
- fix deadlock during file transfer via rsync/krsh
- thanks goes to James Antil for hint

* Fri Nov 26 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.5-6
- rebuild

* Mon Nov 22 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.5-3
- fix predictable-tempfile-name bug in krb5-send-pr (CAN-2004-0971, #140036)

* Tue Nov 16 2004 Nalin Dahyabhai <nalin@redhat.com>
- silence compiler warning in kprop by using an in-memory ccache with a fixed
  name instead of an on-disk ccache with a name generated by tmpnam()

* Tue Nov 16 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.5-2
- fix globbing patch port mode (#139075)

* Mon Nov  1 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.5-1
- fix segfault in telnet due to incorrect checking of gethostbyname_r result
  codes (#129059)

* Fri Oct 15 2004 Nalin Dahyabhai <nalin@redhat.com>
- remove rc4-hmac:norealm and rc4-hmac:onlyrealm from the default list of
  supported keytypes in kdc.conf -- they produce exactly the same keys as
  rc4-hmac:normal because rc4 string-to-key ignores salts
- nuke kdcrotate -- there are better ways to balance the load on KDCs, and
  the SELinux policy for it would have been scary-looking
- update to 1.3.5, mainly to include MITKRB5SA 2004-002 and 2004-003

* Tue Aug 31 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-7
- rebuild

* Tue Aug 24 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-6
- rebuild

* Tue Aug 24 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-5
- incorporate revised fixes from Tom Yu for CAN-2004-0642, CAN-2004-0644,
  CAN-2004-0772

* Mon Aug 23 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-4
- rebuild

* Mon Aug 23 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-3
- incorporate fixes from Tom Yu for CAN-2004-0642, CAN-2004-0772
  (MITKRB5-SA-2004-002, #130732)
- incorporate fixes from Tom Yu for CAN-2004-0644 (MITKRB5-SA-2004-003, #130732)

* Tue Jul 27 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-2
- fix indexing error in server sorting patch (#127336)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun 14 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-0.1
- update to 1.3.4 final

* Mon Jun  7 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.4-0
- update to 1.3.4 beta1
- remove MITKRB5-SA-2004-001, included in 1.3.4

* Mon Jun  7 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-8
- rebuild

* Fri Jun  4 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-7
- rebuild

* Fri Jun  4 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-6
- apply updated patch from MITKRB5-SA-2004-001 (revision 2004-06-02)

* Tue Jun  1 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-5
- rebuild

* Tue Jun  1 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-4
- apply patch from MITKRB5-SA-2004-001 (#125001)

* Wed May 12 2004 Thomas Woerner <twoerner@redhat.com> 1.3.3-3
- removed rpath

* Thu Apr 15 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-2
- re-enable large file support, fell out in 1.3-1
- patch rcp to use long long and %%lld format specifiers when reporting file
  sizes on large files

* Tue Apr 13 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.3-1
- update to 1.3.3

* Wed Mar 10 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.2-1
- update to 1.3.2

* Mon Mar  8 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-12
- rebuild

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com> 1.3.1-11.1
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com> 1.3.1-11
- rebuilt

* Mon Feb  9 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-10
- catch krb4 send_to_kdc cases in kdc preference patch

* Mon Feb  2 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-9
- remove patch to set TERM in klogind which, combined with the upstream fix in
  1.3.1, actually produces the bug now (#114762)

* Mon Jan 19 2004 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-8
- when iterating over lists of interfaces which are "up" from getifaddrs(),
  skip over those which have no address (#113347)

* Mon Jan 12 2004 Nalin Dahyabhai <nalin@redhat.com>
- prefer the kdc which last replied to a request when sending requests to kdcs

* Mon Nov 24 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-7
- fix combination of --with-netlib and --enable-dns (#82176)

* Tue Nov 18 2003 Nalin Dahyabhai <nalin@redhat.com>
- remove libdefault ticket_lifetime option from the default krb5.conf, it is
  ignored by libkrb5

* Thu Sep 25 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-6
- fix bug in patch to make rlogind start login with a clean environment a la
  netkit rlogin, spotted and fixed by Scott McClung

* Tue Sep 23 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-5
- include profile.d scriptlets in krb5-devel so that krb5-config will be in
  the path if krb5-workstation isn't installed, reported by Kir Kolyshkin

* Mon Sep  8 2003 Nalin Dahyabhai <nalin@redhat.com>
- add more etypes (arcfour) to the default enctype list in kdc.conf
- don't apply previous patch, refused upstream

* Fri Sep  5 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-4
- fix 32/64-bit bug storing and retrieving the issue_date in v4 credentials

* Wed Sep 3 2003 Dan Walsh <dwalsh@redhat.com> 1.3.1-3
- Don't check for write access on /etc/krb5.conf if SELinux

* Tue Aug 26 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-2
- fixup some int/pointer varargs wackiness

* Tue Aug  5 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-1
- rebuild

* Mon Aug  4 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3.1-0
- update to 1.3.1

* Thu Jul 24 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3-2
- pull fix for non-compliant encoding of salt field in etype-info2 preauth
  data from 1.3.1 beta 1, until 1.3.1 is released.

* Mon Jul 21 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3-1
- update to 1.3

* Mon Jul  7 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.8-4
- correctly use stdargs

* Wed Jun 18 2003 Nalin Dahyabhai <nalin@redhat.com> 1.3-0.beta.4
- test update to 1.3 beta 4
- ditch statglue build option
- krb5-devel requires e2fsprogs-devel, which now provides libss and libcom_err

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 21 2003 Jeremy Katz <katzj@redhat.com> 1.2.8-2
- gcc 3.3 doesn't implement varargs.h, include stdarg.h instead

* Wed Apr  9 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.8-1
- update to 1.2.8

* Mon Mar 31 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-14
- fix double-free of enc_part2 in krb524d

* Fri Mar 21 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-13
- update to latest patch kit for MITKRB5-SA-2003-004

* Wed Mar 19 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-12
- add patch included in MITKRB5-SA-2003-003 (CAN-2003-0028)

* Mon Mar 17 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-11
- add patches from patchkit from MITKRB5-SA-2003-004 (CAN-2003-0138 and
  CAN-2003-0139)

* Thu Mar  6 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-10
- rebuild

* Thu Mar  6 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-9
- fix buffer underrun in unparsing certain principals (CAN-2003-0082)

* Tue Feb  4 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-8
- add patch to document the reject-bad-transited option in kdc.conf

* Mon Feb  3 2003 Nalin Dahyabhai <nalin@redhat.com>
- add patch to fix server-side crashes when principals have no
  components (CAN-2003-0072)

* Thu Jan 23 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-7
- add patch from Mark Cox for exploitable bugs in ftp client

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 15 2003 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-5
- use PICFLAGS when building code from the ktany patch

* Thu Jan  9 2003 Bill Nottingham <notting@redhat.com> 1.2.7-4
- debloat

* Tue Jan  7 2003 Jeremy Katz <katzj@redhat.com> 1.2.7-3
- include .so.* symlinks as well as .so.*.*

* Mon Dec  9 2002 Jakub Jelinek <jakub@redhat.com> 1.2.7-2
- always #include <errno.h> to access errno, never do it directly
- enable LFS on a bunch of other 32-bit arches

* Wed Dec  4 2002 Nalin Dahyabhai <nalin@redhat.com>
- increase the maximum name length allowed by kuserok() to the higher value
  used in development versions

* Mon Dec  2 2002 Nalin Dahyabhai <nalin@redhat.com>
- install src/krb524/README as README.krb524 in the -servers package,
  includes information about converting for AFS principals

* Fri Nov 15 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.7-1
- update to 1.2.7
- disable use of tcl

* Mon Nov 11 2002 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.2.7-beta2 (internal only, not for release), dropping dnsparse
  and kadmind4 fixes

* Wed Oct 23 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.6-5
- add patch for buffer overflow in kadmind4 (not used by default)

* Fri Oct 11 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.6-4
- drop a hunk from the dnsparse patch which is actually redundant (thanks to
  Tom Yu)

* Wed Oct  9 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.6-3
- patch to handle truncated dns responses

* Mon Oct  7 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.6-2
- remove hashless key types from the default kdc.conf, they're not supposed to
  be there, noted by Sam Hartman on krbdev

* Fri Sep 27 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.6-1
- update to 1.2.6

* Fri Sep 13 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.5-7
- use %%{_lib} for the sake of multilib systems

* Fri Aug  2 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.5-6
- add patch from Tom Yu for exploitable bugs in rpc code used in kadmind

* Tue Jul 23 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.5-5
- fix bug in krb5.csh which would cause the path check to always succeed

* Fri Jul 19 2002 Jakub Jelinek <jakub@redhat.com> 1.2.5-4
- build even libdb.a with -fPIC and $RPM_OPT_FLAGS.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed May  1 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.5-1
- update to 1.2.5
- disable statglue

* Fri Mar  1 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.4-1
- update to 1.2.4

* Wed Feb 20 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.3-5
- rebuild in new environment
- reenable statglue

* Sat Jan 26 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- prereq chkconfig for the server subpackage

* Wed Jan 16 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.3-3
- build without -g3, which gives us large static libraries in -devel

* Tue Jan 15 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.3-2
- reintroduce ld.so.conf munging in the -libs %%post

* Thu Jan 10 2002 Nalin Dahyabhai <nalin@redhat.com> 1.2.3-1
- rename the krb5 package back to krb5-libs; the previous rename caused
  something of an uproar
- update to 1.2.3, which includes the FTP and telnetd fixes
- configure without --enable-dns-for-kdc --enable-dns-for-realm, which now set
  the default behavior instead of enabling the feature (the feature is enabled
  by --enable-dns, which we still use)
- reenable optimizations on Alpha
- support more encryption types in the default kdc.conf (heads-up from post
  to comp.protocols.kerberos by Jason Heiss)

* Fri Aug  3 2001 Nalin Dahyabhai <nalin@redhat.com> 1.2.2-14
- rename the krb5-libs package to krb5 (naming a subpackage -libs when there
  is no main package is silly)
- move defaults for PAM to the appdefaults section of krb5.conf -- this is
  the area where the krb5_appdefault_* functions look for settings)
- disable statglue (warning: breaks binary compatibility with previous
  packages, but has to be broken at some point to work correctly with
  unpatched versions built with newer versions of glibc)

* Fri Aug  3 2001 Nalin Dahyabhai <nalin@redhat.com> 1.2.2-13
- bump release number and rebuild

* Wed Aug  1 2001 Nalin Dahyabhai <nalin@redhat.com>
- add patch to fix telnetd vulnerability

* Fri Jul 20 2001 Nalin Dahyabhai <nalin@redhat.com>
- tweak statglue.c to fix stat/stat64 aliasing problems
- be cleaner in use of gcc to build shlibs

* Wed Jul 11 2001 Nalin Dahyabhai <nalin@redhat.com>
- use gcc to build shared libraries

* Wed Jun 27 2001 Nalin Dahyabhai <nalin@redhat.com>
- add patch to support "ANY" keytab type (i.e.,
  "default_keytab_name = ANY:FILE:/etc/krb5.keytab,SRVTAB:/etc/srvtab"
  patch from Gerald Britton, #42551)
- build with -D_FILE_OFFSET_BITS=64 to get large file I/O in ftpd (#30697)
- patch ftpd to use long long and %%lld format specifiers to support the SIZE
  command on large files (also #30697)
- don't use LOG_AUTH as an option value when calling openlog() in ksu (#45965)
- implement reload in krb5kdc and kadmind init scripts (#41911)
- lose the krb5server init script (not using it any more)

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Tue May 29 2001 Nalin Dahyabhai <nalin@redhat.com>
- pass some structures by address instead of on the stack in krb5kdc

* Tue May 22 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Thu Apr 26 2001 Nalin Dahyabhai <nalin@redhat.com>
- add patch from Tom Yu to fix ftpd overflows (#37731)

* Wed Apr 18 2001 Than Ngo <than@redhat.com>
- disable optimizations on the alpha again

* Fri Mar 30 2001 Nalin Dahyabhai <nalin@redhat.com>
- add in glue code to make sure that libkrb5 continues to provide a
  weak copy of stat()

* Thu Mar 15 2001 Nalin Dahyabhai <nalin@redhat.com>
- build alpha with -O0 for now

* Thu Mar  8 2001 Nalin Dahyabhai <nalin@redhat.com>
- fix the kpropd init script

* Mon Mar  5 2001 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.2.2, which fixes some bugs relating to empty ETYPE-INFO
- re-enable optimization on Alpha

* Thu Feb  8 2001 Nalin Dahyabhai <nalin@redhat.com>
- build alpha with -O0 for now
- own %{_var}/kerberos

* Tue Feb  6 2001 Nalin Dahyabhai <nalin@redhat.com>
- own the directories which are created for each package (#26342)

* Tue Jan 23 2001 Nalin Dahyabhai <nalin@redhat.com>
- gettextize init scripts

* Fri Jan 19 2001 Nalin Dahyabhai <nalin@redhat.com>
- add some comments to the ksu patches for the curious
- re-enable optimization on alphas

* Mon Jan 15 2001 Nalin Dahyabhai <nalin@redhat.com>
- fix krb5-send-pr (#18932) and move it from -server to -workstation
- buildprereq libtermcap-devel
- temporariliy disable optimization on alphas
- gettextize init scripts

* Tue Dec  5 2000 Nalin Dahyabhai <nalin@redhat.com>
- force -fPIC

* Fri Dec  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Tue Oct 31 2000 Nalin Dahyabhai <nalin@redhat.com>
- add bison as a BuildPrereq (#20091)

* Mon Oct 30 2000 Nalin Dahyabhai <nalin@redhat.com>
- change /usr/dict/words to /usr/share/dict/words in default kdc.conf (#20000)

* Thu Oct  5 2000 Nalin Dahyabhai <nalin@redhat.com>
- apply kpasswd bug fixes from David Wragg

* Wed Oct  4 2000 Nalin Dahyabhai <nalin@redhat.com>
- make krb5-libs obsolete the old krb5-configs package (#18351)
- don't quit from the kpropd init script if there's no principal database so
  that you can propagate the first time without running kpropd manually
- don't complain if /etc/ld.so.conf doesn't exist in the -libs %post

* Tue Sep 12 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix credential forwarding problem in klogind (goof in KRB5CCNAME handling)
  (#11588)
- fix heap corruption bug in FTP client (#14301)

* Wed Aug 16 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix summaries and descriptions
- switched the default transfer protocol from PORT to PASV as proposed on
  bugzilla (#16134), and to match the regular ftp package's behavior

* Wed Jul 19 2000 Jeff Johnson <jbj@redhat.com>
- rebuild to compress man pages.

* Sat Jul 15 2000 Bill Nottingham <notting@redhat.com>
- move initscript back

* Fri Jul 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- disable servers by default to keep linuxconf from thinking they need to be
  started when they don't

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jul 10 2000 Nalin Dahyabhai <nalin@redhat.com>
- change cleanup code in post to not tickle chkconfig
- add grep as a Prereq: for -libs

* Thu Jul  6 2000 Nalin Dahyabhai <nalin@redhat.com>
- move condrestarts to postun
- make xinetd configs noreplace
- add descriptions to xinetd configs
- add /etc/init.d as a prereq for the -server package
- patch to properly truncate $TERM in krlogind

* Fri Jun 30 2000 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.2.1
- back out Tom Yu's patch, which is a big chunk of the 1.2 -> 1.2.1 update
- start using the official source tarball instead of its contents

* Thu Jun 29 2000 Nalin Dahyabhai <nalin@redhat.com>
- Tom Yu's patch to fix compatibility between 1.2 kadmin and 1.1.1 kadmind
- pull out 6.2 options in the spec file (sonames changing in 1.2 means it's not
  compatible with other stuff in 6.2, so no need)

* Wed Jun 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- tweak graceful start/stop logic in post and preun

* Mon Jun 26 2000 Nalin Dahyabhai <nalin@redhat.com>
- update to the 1.2 release
- ditch a lot of our patches which went upstream
- enable use of DNS to look up things at build-time
- disable use of DNS to look up things at run-time in default krb5.conf
- change ownership of the convert-config-files script to root.root
- compress PS docs
- fix some typos in the kinit man page
- run condrestart in server post, and shut down in preun

* Mon Jun 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- only remove old krb5server init script links if the init script is there

* Sat Jun 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- disable kshell and eklogin by default

* Thu Jun 15 2000 Nalin Dahyabhai <nalin@redhat.com>
- patch mkdir/rmdir problem in ftpcmd.y
- add condrestart option to init script
- split the server init script into three pieces and add one for kpropd

* Wed Jun 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- make sure workstation servers are all disabled by default
- clean up krb5server init script

* Fri Jun  9 2000 Nalin Dahyabhai <nalin@redhat.com>
- apply second set of buffer overflow fixes from Tom Yu
- fix from Dirk Husung for a bug in buffer cleanups in the test suite
- work around possibly broken rev binary in running test suite
- move default realm configs from /var/kerberos to %{_var}/kerberos

* Tue Jun  6 2000 Nalin Dahyabhai <nalin@redhat.com>
- make ksu and v4rcp owned by root

* Sat Jun  3 2000 Nalin Dahyabhai <nalin@redhat.com>
- use %%{_infodir} to better comply with FHS
- move .so files to -devel subpackage
- tweak xinetd config files (bugs #11833, #11835, #11836, #11840)
- fix package descriptions again

* Wed May 24 2000 Nalin Dahyabhai <nalin@redhat.com>
- change a LINE_MAX to 1024, fix from Ken Raeburn
- add fix for login vulnerability in case anyone rebuilds without krb4 compat
- add tweaks for byte-swapping macros in krb.h, also from Ken
- add xinetd config files
- make rsh and rlogin quieter
- build with debug to fix credential forwarding
- add rsh as a build-time req because the configure scripts look for it to
  determine paths

* Wed May 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix config_subpackage logic

* Tue May 16 2000 Nalin Dahyabhai <nalin@redhat.com>
- remove setuid bit on v4rcp and ksu in case the checks previously added
  don't close all of the problems in ksu
- apply patches from Jeffrey Schiller to fix overruns Chris Evans found
- reintroduce configs subpackage for use in the errata
- add PreReq: sh-utils

* Mon May 15 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix double-free in the kdc (patch merged into MIT tree)
- include convert-config-files script as a documentation file

* Wed May 03 2000 Nalin Dahyabhai <nalin@redhat.com>
- patch ksu man page because the -C option never works
- add access() checks and disable debug mode in ksu
- modify default ksu build arguments to specify more directories in CMD_PATH
  and to use getusershell()

* Wed May 03 2000 Bill Nottingham <notting@redhat.com>
- fix configure stuff for ia64

* Mon Apr 10 2000 Nalin Dahyabhai <nalin@redhat.com>
- add LDCOMBINE=-lc to configure invocation to use libc versioning (bug #10653)
- change Requires: for/in subpackages to include %{version}

* Wed Apr 05 2000 Nalin Dahyabhai <nalin@redhat.com>
- add man pages for kerberos(1), kvno(1), .k5login(5)
- add kvno to -workstation

* Mon Apr 03 2000 Nalin Dahyabhai <nalin@redhat.com>
- Merge krb5-configs back into krb5-libs.  The krb5.conf file is marked as
  a %%config file anyway.
- Make krb5.conf a noreplace config file.

* Thu Mar 30 2000 Nalin Dahyabhai <nalin@redhat.com>
- Make klogind pass a clean environment to children, like NetKit's rlogind does.

* Wed Mar 08 2000 Nalin Dahyabhai <nalin@redhat.com>
- Don't enable the server by default.
- Compress info pages.
- Add defaults for the PAM module to krb5.conf

* Mon Mar 06 2000 Nalin Dahyabhai <nalin@redhat.com>
- Correct copyright: it's exportable now, provided the proper paperwork is
  filed with the government.

* Fri Mar 03 2000 Nalin Dahyabhai <nalin@redhat.com>
- apply Mike Friedman's patch to fix format string problems
- don't strip off argv[0] when invoking regular rsh/rlogin

* Thu Mar 02 2000 Nalin Dahyabhai <nalin@redhat.com>
- run kadmin.local correctly at startup

* Mon Feb 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- pass absolute path to kadm5.keytab if/when extracting keys at startup

* Sat Feb 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix info page insertions

* Wed Feb  9 2000 Nalin Dahyabhai <nalin@redhat.com>
- tweak server init script to automatically extract kadm5 keys if
  /var/kerberos/krb5kdc/kadm5.keytab doesn't exist yet
- adjust package descriptions

* Thu Feb  3 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix for potentially gzipped man pages

* Fri Jan 21 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix comments in krb5-configs

* Fri Jan  7 2000 Nalin Dahyabhai <nalin@redhat.com>
- move /usr/kerberos/bin to end of PATH

* Tue Dec 28 1999 Nalin Dahyabhai <nalin@redhat.com>
- install kadmin header files

* Tue Dec 21 1999 Nalin Dahyabhai <nalin@redhat.com>
- patch around TIOCGTLC defined on alpha and remove warnings from libpty.h
- add installation of info docs
- remove krb4 compat patch because it doesn't fix workstation-side servers

* Mon Dec 20 1999 Nalin Dahyabhai <nalin@redhat.com>
- remove hesiod dependency at build-time

* Sun Dec 19 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- rebuild on 1.1.1

* Thu Oct  7 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- clean up init script for server, verify that it works [jlkatz]
- clean up rotation script so that rc likes it better
- add clean stanza

* Mon Oct  4 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- backed out ncurses and makeshlib patches
- update for krb5-1.1
- add KDC rotation to rc.boot, based on ideas from Michael's C version

* Mon Sep 26 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- added -lncurses to telnet and telnetd makefiles

* Mon Jul  5 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- added krb5.csh and krb5.sh to /etc/profile.d

* Mon Jun 22 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- broke out configuration files

* Mon Jun 14 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- fixed server package so that it works now

* Sat May 15 1999 Nalin Dahyabhai <nsdahya1@eos.ncsu.edu>
- started changelog (previous package from zedz.net)
- updated existing 1.0.5 RPM from Eos Linux to krb5 1.0.6
- added --force to makeinfo commands to skip errors during build

%prep
%setup -q
%patch2  -p1 -b .manpage-paths
%patch3  -p1 -b .netkit-rsh
%patch4  -p1 -b .rlogind-environ
%patch5  -p1 -b .ksu-access
%patch6  -p1 -b .ksu-path
%patch9  -p1 -b .brokenrev
%patch11 -p1 -b .passive
%patch12 -p1 -b .ktany
%patch13 -p1 -b .large-file
%patch14 -p1 -b .ftp-glob
%patch15 -p1 -b .check
%patch16 -p1 -b .no-rpath
%patch18 -p1 -b .reject-bad-transited
%if %{WITH_SELINUX}
%patch21 -p1 -b .selinux
%endif
%patch23 -p1 -b .dns
%patch25 -p1 -b .null
# Removes a malloc(0) case, nothing more.
# %patch26 -p1 -b .efence
%patch27 -p1 -b .rcp-sendlarge
%patch29 -p1 -b .kprop-mktemp
%patch30 -p1 -b .send-pr-tempfile
%patch32 -p1 -b .ncurses
%patch33 -p1 -b .io
%patch35 -p1 -b .fclose
%patch36 -p1 -b .rcp-markus
%patch39 -p1 -b .api
%patch40 -p1 -b .telnet-environ
%patch41 -p1 -b .login-lpass
%patch44 -p1 -b .enospc
%patch45 -p1 -b .gssinit
pushd src
%patch46 -p0 -b .2006-001
popd
cp src/krb524/README README.krb524
gzip doc/*.ps
%patch1000 -p1 -b .scripts
cd src
top=`pwd`
for configurein in `find -name configure.in -type f` ; do
	pushd `dirname $configurein`
	autoconf -I "$top"
	popd
done

%build
cd src
INCLUDES=-I%{_includedir}/et
# Get LFS support on systems that need it which aren't already 64-bit.
%ifarch %{ix86} s390 ppc sparc
DEFINES="-D_FILE_OFFSET_BITS=64" ; export DEFINES
%endif
CFLAGS="`echo $RPM_OPT_FLAGS $DEFINES $INCLUDES -fPIC`"
CPPFLAGS="`echo $DEFINES $INCLUDES`"
%configure \
	CC=%{__cc} \
	CFLAGS="$CFLAGS" \
	LDFLAGS="-pie" \
	CPPFLAGS="$CPPFLAGS" \
	SS_LIB="-lss -lcurses" \
	--enable-shared --enable-static \
	--bindir=%{krb5prefix}/bin \
	--mandir=%{krb5prefix}/man \
	--sbindir=%{krb5prefix}/sbin \
	--datadir=%{krb5prefix}/share \
	--localstatedir=%{_var}/kerberos \
	--with-krb4 \
	--with-system-et \
	--with-system-ss \
	--with-netlib=-lresolv \
	--without-tcl \
	--enable-dns
# Now build it.  Override the RPATH_FLAG and PROG_LIBPATH to drop the rpath, and
# override LDCOMBINE to use gcc instead of ld to build shared libraries.
make	RPATH_FLAG= PROG_RPATH= \
	OBJLISTS="OBJS.ST OBJS.SH" \
	LDCOMBINE='%{__cc} -shared -Wl,-soname=lib$(LIB)$(SHLIBSEXT) $(CFLAGS)'

# Run the test suite.
: make	RPATH_FLAG= PROG_RPATH= check TMPDIR=%{_tmppath}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Shell scripts wrappers for Kerberized rsh and rlogin.
mkdir -p $RPM_BUILD_ROOT%{krb5prefix}/bin
install -m 755 $RPM_SOURCE_DIR/{krsh,krlogin} $RPM_BUILD_ROOT/%{krb5prefix}/bin/

# Info docs.
mkdir -p $RPM_BUILD_ROOT%{_infodir}
install -m 644 doc/*.info* $RPM_BUILD_ROOT%{_infodir}/
# Forcefully compress the info pages so that we know the right file name to
# pass to install-info in %%post.
gzip $RPM_BUILD_ROOT%{_infodir}/*.info*

# Sample KDC config files.
mkdir -p $RPM_BUILD_ROOT%{_var}/kerberos/krb5kdc
install -m 644 $RPM_SOURCE_DIR/kdc.conf  $RPM_BUILD_ROOT%{_var}/kerberos/krb5kdc/
install -m 644 $RPM_SOURCE_DIR/kadm5.acl $RPM_BUILD_ROOT%{_var}/kerberos/krb5kdc/

# Login-time scriptlets to fix the PATH variable.
mkdir -p $RPM_BUILD_ROOT/etc/profile.d
install -m 644 $RPM_SOURCE_DIR/krb5.conf $RPM_BUILD_ROOT/etc/krb5.conf
install -m 755 $RPM_SOURCE_DIR/krb5.{sh,csh} $RPM_BUILD_ROOT/etc/profile.d/

# Server init scripts.
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
install -m 755 $RPM_SOURCE_DIR/krb5kdc.init $RPM_BUILD_ROOT/etc/rc.d/init.d/krb5kdc
install -m 755 $RPM_SOURCE_DIR/kadmind.init $RPM_BUILD_ROOT/etc/rc.d/init.d/kadmin
install -m 755 $RPM_SOURCE_DIR/kpropd.init $RPM_BUILD_ROOT/etc/rc.d/init.d/kprop
install -m 755 $RPM_SOURCE_DIR/krb524d.init $RPM_BUILD_ROOT/etc/rc.d/init.d/krb524
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
install -m 644 $RPM_SOURCE_DIR/krb5kdc.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/krb5kdc
install -m 644 $RPM_SOURCE_DIR/kadmin.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/kadmin
install -m 644 $RPM_SOURCE_DIR/krb524.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/krb524

# Xinetd configuration files.
mkdir -p $RPM_BUILD_ROOT/etc/xinetd.d/
for xinetd in eklogin klogin kshell ekrb5-telnet krb5-telnet gssftp ; do
	install -m 644 $RPM_SOURCE_DIR/${xinetd}.xinetd \
	$RPM_BUILD_ROOT/etc/xinetd.d/${xinetd}
done

# The rest of the binaries, headers, libraries, and docs.
make -C src DESTDIR=$RPM_BUILD_ROOT install

# Fixup permissions on header files.
find $RPM_BUILD_ROOT/%{_includedir} -type d | xargs chmod 755
find $RPM_BUILD_ROOT/%{_includedir} -type f | xargs chmod 644

# Fixup strange shared library permissions.
chmod 755 $RPM_BUILD_ROOT%{_libdir}/*.so{,.*}

# Munge the krb5-config script to remove rpaths.
sed "s|^CC_LINK=.*|CC_LINK='\$(CC) \$(PROG_LIBPATH)'|g" src/krb5-config > $RPM_BUILD_ROOT%{krb5prefix}/bin/krb5-config

# Munge krb5-config yet again.  This is totally wrong for 64-bit, but chunks
# of the no-rpath patch already conspire to strip out /usr/<anything> from the
# list of link flags.
sed -r -i -e 's|^libdir=/usr/lib(64)?$|libdir=/usr/lib|g' $RPM_BUILD_ROOT%{krb5prefix}/bin/krb5-config

# Remove the randomly-generated compile-et filename comment from header files.
sed -i -e 's|^ \* ettmp[^ \t]*\.h:$| * ettmpXXXXXX.h:|g' $RPM_BUILD_ROOT%{_includedir}/*{,/*}.h

%if %{install_macro}
# Install the autoconf macro.
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/aclocal
install -m644 src/util/ac_check_krb5.m4 $RPM_BUILD_ROOT/%{_datadir}/aclocal/
%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post server
# Remove the init script for older servers.
[ -x /etc/rc.d/init.d/krb5server ] && /sbin/chkconfig --del krb5server
# Install the new ones.
/sbin/chkconfig --add krb5kdc
/sbin/chkconfig --add kadmin
/sbin/chkconfig --add krb524
/sbin/chkconfig --add kprop
# Install info pages.
/sbin/install-info %{_infodir}/krb425.info.gz %{_infodir}/dir
/sbin/install-info %{_infodir}/krb5-admin.info.gz %{_infodir}/dir
/sbin/install-info %{_infodir}/krb5-install.info.gz %{_infodir}/dir

%preun server
if [ "$1" = "0" ] ; then
	/sbin/chkconfig --del krb5kdc
	/sbin/chkconfig --del kadmin
	/sbin/chkconfig --del krb524
	/sbin/chkconfig --del kprop
	/sbin/service krb5kdc stop > /dev/null 2>&1 || :
	/sbin/service kadmin stop > /dev/null 2>&1 || :
	/sbin/service krb524 stop > /dev/null 2>&1 || :
	/sbin/service kprop stop > /dev/null 2>&1 || :
	/sbin/install-info --delete %{_infodir}/krb425.info.gz %{_infodir}/dir
	/sbin/install-info --delete %{_infodir}/krb5-admin.info.gz %{_infodir}/dir
	/sbin/install-info --delete %{_infodir}/krb5-install.info.gz %{_infodir}/dir
fi

%postun server
if [ "$1" -ge 1 ] ; then
	/sbin/service krb5kdc condrestart > /dev/null 2>&1 || :
	/sbin/service kadmin condrestart > /dev/null 2>&1 || :
	/sbin/service krb524 condrestart > /dev/null 2>&1 || :
	/sbin/service kprop condrestart > /dev/null 2>&1 || :
fi

%post workstation
/sbin/install-info %{_infodir}/krb5-user.info %{_infodir}/dir
/sbin/service xinetd reload > /dev/null 2>&1 || :

%preun workstation
if [ "$1" = "0" ] ; then
	/sbin/install-info --delete %{_infodir}/krb5-user.info %{_infodir}/dir
fi

%postun workstation
/sbin/service xinetd reload > /dev/null 2>&1 || :

%files workstation
%defattr(-,root,root)

%config(noreplace) /etc/profile.d/krb5.sh
%config(noreplace) /etc/profile.d/krb5.csh

%config(noreplace) /etc/xinetd.d/*

%docdir %{krb5prefix}/man
%doc doc/krb5-user/*.html doc/user*.ps.gz src/config-files/services.append
%doc doc/{ftp,kdestroy,kinit,klist,kpasswd,ksu,rcp,rlogin,rsh,telnet}.html
%attr(0755,root,root) %doc src/config-files/convert-config-files
%{_infodir}/krb5-user.info*

%dir %{krb5prefix}
%dir %{krb5prefix}/bin
%dir %{krb5prefix}/man
%dir %{krb5prefix}/man/man1
%dir %{krb5prefix}/man/man5
%dir %{krb5prefix}/man/man8
%dir %{krb5prefix}/sbin

%{krb5prefix}/bin/ftp
%{krb5prefix}/man/man1/ftp.1*
%{krb5prefix}/bin/gss-client
%{krb5prefix}/bin/kdestroy
%{krb5prefix}/man/man1/kdestroy.1*
%{krb5prefix}/man/man1/kerberos.1*
%{krb5prefix}/bin/kinit
%{krb5prefix}/man/man1/kinit.1*
%{krb5prefix}/bin/klist
%{krb5prefix}/man/man1/klist.1*
%{krb5prefix}/bin/kpasswd
%{krb5prefix}/man/man1/kpasswd.1*
%{krb5prefix}/bin/krb524init
%{krb5prefix}/man/man1/krb524init.1*
%{krb5prefix}/sbin/k5srvutil
%{krb5prefix}/man/man8/k5srvutil.8*
%{krb5prefix}/sbin/kadmin
%{krb5prefix}/man/man8/kadmin.8*
%{krb5prefix}/sbin/ktutil
%{krb5prefix}/man/man8/ktutil.8*
%attr(4755,root,root) %{krb5prefix}/bin/ksu
%{krb5prefix}/man/man1/ksu.1*
%{krb5prefix}/bin/kvno
%{krb5prefix}/man/man1/kvno.1*
%{krb5prefix}/bin/rcp
%{krb5prefix}/man/man1/rcp.1*
%{krb5prefix}/bin/krlogin
%{krb5prefix}/bin/rlogin
%{krb5prefix}/man/man1/rlogin.1*
%{krb5prefix}/bin/krsh
%{krb5prefix}/bin/rsh
%{krb5prefix}/man/man1/rsh.1*
%{krb5prefix}/bin/telnet
%{krb5prefix}/man/man1/telnet.1*
%{krb5prefix}/man/man1/tmac.doc*
%attr(0755,root,root) %{krb5prefix}/bin/v4rcp
%{krb5prefix}/man/man1/v4rcp.1*
%{krb5prefix}/bin/sim_client
%{krb5prefix}/bin/uuclient
%{krb5prefix}/sbin/login.krb5
%{krb5prefix}/man/man8/login.krb5.8*
%{krb5prefix}/sbin/ftpd
%{krb5prefix}/man/man8/ftpd.8*
%{krb5prefix}/sbin/gss-server
%{krb5prefix}/sbin/klogind
%{krb5prefix}/man/man8/klogind.8*
%{krb5prefix}/sbin/krb5-send-pr
%{krb5prefix}/man/man1/krb5-send-pr.1*
%{krb5prefix}/sbin/kshd
%{krb5prefix}/man/man8/kshd.8*
%{krb5prefix}/sbin/telnetd
%{krb5prefix}/man/man8/telnetd.8*
%{krb5prefix}/sbin/uuserver
%{krb5prefix}/man/man5/.k5login.5*
%{krb5prefix}/man/man5/krb5.conf.5*

%files server
%defattr(-,root,root)

%config /etc/rc.d/init.d/krb5kdc
%config /etc/rc.d/init.d/kadmin
%config /etc/rc.d/init.d/krb524
%config /etc/rc.d/init.d/kprop
%config(noreplace) /etc/sysconfig/krb5kdc
%config(noreplace) /etc/sysconfig/kadmin
%config(noreplace) /etc/sysconfig/krb524

%docdir %{krb5prefix}/man
%doc doc/admin*.ps.gz doc/krb5-admin/*.html
%doc doc/krb425*.ps.gz doc/krb425/*.html
%doc doc/install*.ps.gz doc/krb5-install/*.html
%doc README.krb524

%{_infodir}/krb5-admin.info*
%{_infodir}/krb5-install.info*
%{_infodir}/krb425.info*

%dir %{_var}/kerberos
%dir %{_var}/kerberos/krb5kdc
%config(noreplace) %{_var}/kerberos/krb5kdc/kdc.conf
%config(noreplace) %{_var}/kerberos/krb5kdc/kadm5.acl

%dir %{krb5prefix}/bin
%dir %{_libdir}/krb5
%dir %{_libdir}/krb5/plugins
%dir %{_libdir}/krb5/plugins/kdb
%{_libdir}/krb5/plugins/kdb/db2.so
%dir %{krb5prefix}/man
%dir %{krb5prefix}/man/man1
%dir %{krb5prefix}/man/man5
%dir %{krb5prefix}/man/man8
%dir %{krb5prefix}/sbin

%{krb5prefix}/man/man5/kdc.conf.5*
%{krb5prefix}/sbin/kadmin.local
%{krb5prefix}/man/man8/kadmin.local.8*
%{krb5prefix}/sbin/kadmind
%{krb5prefix}/man/man8/kadmind.8*
%{krb5prefix}/sbin/kdb5_util
%{krb5prefix}/man/man8/kdb5_util.8*
%{krb5prefix}/sbin/kprop
%{krb5prefix}/man/man8/kprop.8*
%{krb5prefix}/sbin/kpropd
%{krb5prefix}/man/man8/kpropd.8*
%{krb5prefix}/sbin/krb524d
%{krb5prefix}/man/man8/krb524d.8*
%{krb5prefix}/sbin/krb5kdc
%{krb5prefix}/man/man8/krb5kdc.8*
%{krb5prefix}/sbin/sim_server
# This is here for people who want to test their server, and also 
# included in devel package for similar reasons.
%{krb5prefix}/bin/sclient
%{krb5prefix}/man/man1/sclient.1*
%{krb5prefix}/sbin/sserver
%{krb5prefix}/man/man8/sserver.8*

%files libs
%defattr(-,root,root)
#%config /etc/rc.d/init.d/kdcrotate
%config(noreplace) /etc/krb5.conf
%docdir %{krb5prefix}/man
%{_libdir}/lib*.so.*
%dir %{_libdir}/krb5
%dir %{_libdir}/krb5/plugins
%{krb5prefix}/share

%files devel
%defattr(-,root,root)

%config(noreplace) /etc/profile.d/krb5.sh
%config(noreplace) /etc/profile.d/krb5.csh

%docdir %{krb5prefix}/man
%doc doc/api
%doc doc/implement
%doc doc/kadm5
%doc doc/kadmin
%doc doc/krb5-protocol
%doc doc/rpc
%doc doc/threads.txt

%dir %{krb5prefix}
%dir %{krb5prefix}/bin
%dir %{krb5prefix}/man
%dir %{krb5prefix}/man/man1
%dir %{krb5prefix}/man/man8
%dir %{krb5prefix}/sbin

%{_includedir}/*
%{_libdir}/lib*.a
%{_libdir}/lib*.so
%if %{install_macro}
%{_datadir}/aclocal/*
%endif

%{krb5prefix}/bin/krb5-config
%{krb5prefix}/bin/sclient
%{krb5prefix}/man/man1/krb5-config.1*
%{krb5prefix}/man/man1/sclient.1*
%{krb5prefix}/man/man8/sserver.8*
%{krb5prefix}/sbin/sserver
