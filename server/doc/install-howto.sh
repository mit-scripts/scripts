# This document is a how-to for installing a Fedora scripts.mit.edu server.
# It is semi-vaguely in the form of a shell script, but is not really
# runnable as it stands.

# Notation
# [PRODUCTION] Production server that will be put into the pool
# [WIZARD]     Semi-production server that will only have
#              daemon.scripts-security-upd bits, among other
#              restricted permissions
# [TESTSERVER] Completely untrusted server

# 'branch' is the current svn branch you are on.  You want to
# use trunk if your just installing a new server, and branches/fcXX-dev
# if your preparing a server on a new Fedora release.
branch="trunk"

# 'server' is the public hostname of your server, for SCP'ing files
# to and from.
server=YOUR-SERVER-NAME-HERE

# ----------------------------->8--------------------------------------
#                       FIRST TIME INSTRUCTIONS
#
# [PRODUCTION] If this is the first time you've installed this hostname,
# you will need to update a bunch of files to add support for it. These
# include:
#   o Adding all aliases to /etc/httpd/conf.d/scripts-vhost-names.conf
#     (usually this is hostname, hostname.mit.edu, h-n, h-n.mit.edu,
#     scriptsN, scriptsN.mit.edu, and the IP address.)
#   o Adding routing rules for the static IP in
#     /etc/sysconfig/network-scripts/route-eth1
#   o Adding the IP address to the hosts file (same hosts as for
#     scripts-vhost-names)
#   o Update SSH config at
#       - server/fedora/config/etc/ssh/shosts.equiv
#       - server/fedora/config/etc/ssh/ssh_known_hosts
#       - server/fedora/config/etc/ssh/sshd_config : DenyUsers
#     (the last part is critical to ensure that rooting one server
#     doesn't give you root to all the other servers)
#   o Put the hostname information in LDAP so SVN and Git work
#   o Set up Nagios monitoring on sipb-noc for the host
#   o Set up the host as in the pool on r-b/r-b /etc/heartbeat/ldirectord.cf
#   o Update locker/etc/known_hosts
#   o Update website files:
#       /mit/scripts/web_scripts/home/server.css.cgi
#       /mit/scripts/web_scripts/heartbeat/heartbeat.php
#
# You will also need to prepare the keytabs for credit-card.  In particular,
# use ktutil to combine the host/scripts.mit.edu and
# host/scripts-vhosts.mit.edu keys with host/this-server.mit.edu in
# the keytab.  Do not use 'k5srvutil change' on the combined keytab
# or you'll break the other servers. (real servers only).  Be
# careful about writing out the keytab: if you write it to an
# existing file the keys will just get appended.  The correct
# credential list should look like:
#   ktutil:  l
#   slot KVNO Principal
#   ---- ---- ---------------------------------------------------------------------
#      1    5 host/old-faithful.mit.edu@ATHENA.MIT.EDU
#      2    3 host/scripts-vhosts.mit.edu@ATHENA.MIT.EDU
#      3    2 host/scripts.mit.edu@ATHENA.MIT.EDU
#      4    8 host/scripts-test.mit.edu@ATHENA.MIT.EDU
#
# The LDAP keytab should be by itself, so be sure to delete it and
# put it in its own file.

# ----------------------------->8--------------------------------------
#                      INFINITE INSTALLATION

# Start with a Scripts kickstarted install of Fedora (install-fedora)

# IMPORTANT: If you are installing a server without the benefit of
# Kickstart (for example, you are installing on XVM, it is VITALLY
# IMPORTANT that you go through the kickstart and apply all of the
# necessary changes--for example, disabling selinux or enabling
# network.)
#   XXX We should make Kickstart work for test servers too

# Make sure selinux is disabled
    selinuxenabled || echo "selinux not enabled"

# Take updates, reboot if there's a kernel update.
    yum update -y

# Get rid of network manager (XXX figure out to make kickstarter do
# this for us)
    yum remove NetworkManager

# Make sure sendmail isn't installed, replace it with postfix
    yum shell <<EOF
remove sendmail
install postfix
run
exit
EOF

# Check out the scripts /etc configuration
    cd /root
    \cp -a etc /
    chmod 0440 /etc/sudoers
    grub2-mkconfig -o /boot/grub2/grub.cfg

# [TEST] You'll need to fix some config now.  See bottom of document.

# Stop /etc/resolv.conf from getting repeatedly overwritten by
# purging DNS servers from ifcfg-eth0 and ifcfg-eth1
    vim /etc/sysconfig/network-scripts/ifcfg-eth0
    vim /etc/sysconfig/network-scripts/ifcfg-eth1

# Make sure network is working.  Kickstart should have
# configured eth0 and eth1 correctly; use service network restart
# to add the new routes from etc in route-eth1.
    systemctl restart network.service
    # Check everything worked:
    route
    ifconfig
    cat /etc/hosts
    cat /etc/sysconfig/network-scripts/route-eth1

# This is the point at which you should start updating scriptsified
# packages for a new Fedora release.  Consult 'upgrade-tips' for more
# information.
    yum install -y scripts-base
    # Some of these packages are naughty and clobber some of our files
    cd /etc
    svn revert resolv.conf hosts sysconfig/openafs nsswitch.conf
    # Troubleshooting: if accountadm, tokensys and nscd fail to install
    # you probably forgot to turn off selinux

# Replace rsyslog with syslog-ng by doing:
    yum shell <<EOF
remove rsyslog
install syslog-ng
run
exit
EOF
    systemctl enable syslog-ng.service

# Install the full list of RPMs that users expect to be on the
# scripts.mit.edu servers.
rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > packages.txt
# arrange for packages.txt to be passed to the server, then run:
    cd /tmp
    yumdownloader --disablerepo=scripts ghc-cgi ghc-cgi-devel
    yum localinstall ghc-cgi*.x86_64.rpm
    yum install -y $(cat packages.txt)
# The reason this works is that ghc-cgi is marked as installonlypkgs
# in yum.conf, telling yum to install them side-by-side rather than
# updating them. If it doesn't work, use --skip-broken on the yum
# command line.

# Check which packages are installed on your new server that are not
# in the snapshot, and remove ones that aren't needed for some reason
# on the new machine.  Otherwise, aside from bloat, you may end up
# with undesirable things for security, like sendmail.
    rpm -qa --queryformat "%{Name}.%{Arch}\n" | grep -v kernel | sort > newpackages.txt
    diff -u packages.txt newpackages.txt | grep -v kernel | less
    # here's a cute script that removes all extra packages
    yum erase -y $(grep -Fxvf packages.txt newpackages.txt)
    # 20101208 - Mysteriously we manage to get these extra packages
    # from kickstart: mcelog mobile-broadband-provider-info
    # ModemManager PackageKit

# ----------------------------->8--------------------------------------
#                      SPHEROID SHENANIGANS

# Install the Python eggs and Ruby gems and PEAR/PECL doohickeys that are on
# the other scripts.mit.edu servers and do not have RPMs.
# The general mode of operation will be to run the "list" command
# on both servers, see what the differences are, check if those diffs
# are packaged up as rpms, and install them (rpm if possible, native otherwise)

# Note: Since ultimately we'd like to move away from using per-language
# package manager and all of these be RPMs, it is of questionable
# importance how much /good/ automation for these is necessary.

# Warning: For a new release, we're supposed to check if Fedora has
# packaged up the RPM.  Unfortunately we don't really have good incants
# for this.

# Warning: If you're installing a new server mid-lifecycle (or even if
# this is the start of a cycle, but you've been staggering the
# installation of servers), upstream may have moved on.  Because we
# don't normally upgrade spheroid projects, that means executing these
# instructions directly means that you will have mismatched versions
# (the new servers will have newer versions.)  Please follow the
# UPGRADE commentary attached to each of these.

# Warning: The package lists that are generated are inconsistent on
# the question of whether or not they contain all packages (locally
# installed as well as distro packaged), or if they just contain locally
# installed packages.  Check this carefully; many of the install incants
# filter out already installed packages.

# PERL CPAN
# ---------

# Install the full list of perl modules that users expect to be on the
# scripts.mit.edu servers.
    cd /root
    export PERL_MM_USE_DEFAULT=1
    cpan # this is interactive, enter the next two lines
        o conf prerequisites_policy follow
        o conf commit
# on a reference server
perldoc -u perllocal | grep head2 | cut -f 3 -d '<' | cut -f 1 -d '|' | sort -u | perl -ne 'chomp; print "notest install $_\n" if system("rpm -q --whatprovides \"perl($_)\" >/dev/null 2>/dev/null")' > perl-packages.txt
# arrange for perl-packages.txt to be transferred to server
    # Package list only contains new packages
    cat perl-packages.txt | perl -MCPAN -e shell
# These are in /usr/local

# UPGRADE: Installing old versions of CPAN modules requires you to
# specify the full path of a module, e.g.
# M/MS/MSCHWERN/Test-Simple-0.62.tar.gz.  It is not currently clear how
# to get this information programatically.  Furthermore, we have a lot
# of CPAN managed modules.  Since CPAN is the only thing
# placed in /usr/local at this point, it may be easier to simple tar and
# cp the Perl modules from one server to another, to keep them
# consistent.  But doing this is fiddly XXX

# PYTHON EGGS
# -----------

# - Look at /usr/lib/python2.7/site-packages and
#           /usr/lib64/python2.7/site-packages for Python eggs and modules.
#   There will be a lot of gunk that was installed from packages;
#   easy-install.pth in /usr/lib/ will tell you what was easy_installed.
#   First use 'yum search' to see if the relevant package is now available
#   as an RPM, and install that if it is.  If not, then use easy_install.
#   Pass -Z to easy_install to install them unzipped, as some zipped eggs
#   want to be able to write to ~/.python-eggs.  (Also makes sourcediving
#   easier.)
# 'easy_install AuthKit jsonlib2 pygit'
cat /usr/lib/python2.7/site-packages/easy-install.pth | grep "^./" | cut -c3- | cut -f1 -d- > egg.txt
    # Package list only contains new packages
    cat egg.txt | xargs easy_install -Z
# These are in /usr

# UPGRADE: Use 'easy_install -n' to see what new versions are installed, and if there
# are updates validate them and upgrade them on the old servers.  Since
# we have a really small package list (around 4) checking these manually
# should be fine.  Note that dry run is slightly buggy and may fail
# midway processing files on account of a missing build directory.

# RUBY GEMS
# ---------

# - Look at `gem list` for Ruby gems.
#   Again, use 'yum search' and prefer RPMs, but failing that, 'gem install'.
#       ezyang: rspec-rails depends on rspec, and will override the Yum
#       package, so... don't use that RPM yet
# XXX This doesn't do the right thing for old version gems
gem list --no-version > gem.txt
    # Package list contains distro gems too
    gem install $(gem list --no-version | grep -Fxvf - gem.txt)
    # Also, we need to install the old rails version
    gem install -v=2.3.14 rails
# These are in /usr

# UPGRADE:  You can either upgrade out-of-date gems, or leave them at
# the old version.  We recommend the latter (see below for the
# rationale), but note that the install script described here doesn't
# pin against version, so you'll need to supply the -v parameters
# manually (the gems we install manually don't move too quickly, so this
# is fairly tractable if you check 'gem outdated'.)
#
# If you want to upgrade, do NOT use wildcard 'gem update'; use 'gem
# outdated' to find out all gems that are out of date, and verify this
# against our locally installed gems (there will be a lot of out of date
# gems, but this is simply because Fedora packaging lags behind the
# canonical versions (this is a good thing).  Manually upgrade just
# those gems.  Note that this doesn't save you from having to install
# old gems on the servers that are being installed out-of-cycle,
# because Ruby supports pinning against old versions, and if those gems
# then mysteriously disappear, things will be sad (note that this isn't
# a *huge* problem, because usually when you pin gems it's in
# conjunction with rvm, so they have their local copy of the gem.)

# PHP PEAR
# --------

# - Look at `pear list` for Pear fruits (or whatever they're called).
#   Yet again, 'yum search' for RPMs before resorting to 'pear install'.  Note
#   that for things in the beta repo, you'll need 'pear install package-beta'.
#   (you might get complaints about the php_scripts module; ignore them)
pear list | tail -n +4 | cut -f 1 -d " " > pear.txt
    # Package list contains distro packages
    pear config-set preferred_state beta
    pear channel-update pear.php.net
    pear install $(pear list | tail -n +4 | cut -f 1 -d " " | grep -Fxvf - pear.txt)
# These are in /usr

# PHP PECL
# --------

# - Look at `pecl list` for PECL things.  'yum search', and if you must,
#   'pecl install' needed items. If it doesn't work, try 'pear install
#   pecl/foo' or 'pecl install foo-beta' or those two combined.
pecl list | tail -n +4 | cut -f 1 -d " " > pecl.txt
    # Package list contains distro packages
    pecl install --nodeps $(pecl list | tail -n +4 | cut -f 1 -d " " | grep -Fxvf - pecl.txt)
# These are in /usr

# ----------------------------->8--------------------------------------
#                       INFINITE CONFIGURATION

# [PROD] Create fedora-ds user (needed for credit-card)
useradd -r -d /var/lib/dirsrv fedora-ds

# Run credit-card to clone in credentials and make things runabble
# NOTE: You may be tempted to run credit-card earlier in the install
# process in order, for example, to be able to SSH in to the servers
# with Kerberos.  However, it is better to install the credentials
# *after* we have run a boatload untrusted code as part of the
# spheroids objects process.  So don't move this step earlier!
python host.py push $server

# This is superseded by credit-card, which works for [PRODUCTION] and
# [WIZARD].  We don't have an easy way of running credit-card for XVM...
#
#   # All types of servers will have an /etc/daemon.keytab file, however,
#   # different types of server will have different credentials in this
#   # keytab.
#   #   [PRODUCTION] daemon.scripts
#   #   [WIZARD]     daemon.scripts-security-upd
#   #   [TESTSERVER] daemon.scripts-test

# Test that zephyr is working
    systemctl enable zhm.service
    systemctl start zhm.service
    echo 'Test!' | zwrite -d -c scripts -i test

# Check out the scripts /usr/vice/etc configuration
    cd /root/vice
    \cp -a etc /usr/vice
# [TESTSERVER] If you're installing a test server, this needs to be
# much smaller; the max filesize on XVM is 10GB.  Pick something like
# 500000. Also, some of the AFS parameters are kind of retarded (and if
# you're low on disk space, will actually exhaust our inodes).  Edit
# these parameters in /etc/sysconfig/openafs (I just chopped a zero
# off of all of our parameters)
    echo "/afs:/usr/vice/cache:500000" > /usr/vice/etc/cacheinfo
    vim /etc/sysconfig/openafs

# [PRODUCTION] Set up replication (see ./install-ldap).
# You'll need the LDAP keytab for this server: be sure to chown it
# fedora-ds after you create the fedora-ds user
    ls -l /etc/dirsrv/keytab
    cat install-ldap

# Enable lots of services (currently in /etc checkout)
    systemctl enable openafs-client.service
    systemctl enable dirsrv.target
    systemctl enable nslcd.service
    systemctl enable nscd.service
    systemctl enable postfix.service
    systemctl enable nrpe.service # chkconfig'd
    systemctl enable httpd.service # not for [WIZARD]

    systemctl start openafs-client.service
    systemctl start dirsrv.target
    systemctl start nslcd.service
    systemctl start nscd.service
    systemctl start postfix.service
    systemctl start nrpe.service
    systemctl start httpd.service # not for [WIZARD]

# Note about OpenAFS: Check that fs sysname is correct.  You should see,
# among others, 'amd64_fedoraX_scripts' (vary X) and 'scripts'. If it's
# not, you probably did a distro upgrade and should update
# tokensys (server/common/oursrc/tokensys/scripts-afsagent-startup.in)
    fs sysname

# Postfix doesn't actually deliver mail; fix this
    cd /etc/postfix
    postmap virtual

# Munin might not be monitoring packages that were installed after it
    munin-node-configure --suggest --shell | sh

# Run fmtutil-sys --all, which does something that makes TeX work.
# (Note: this errors on XeTeX which is ok.)
    fmtutil-sys --all

# Check for unwanted setuid/setgid binaries
    find / -xdev -not -perm -o=x -prune -o -type f -perm /ug=s -print | grep -Fxvf /etc/scripts/allowed-setugid.list
    find / -xdev -not -perm -o=x -prune -o -type f -print0 | xargs -0r /usr/sbin/getcap | cut -d' ' -f1 | grep -Fxvf /etc/scripts/allowed-filecaps.list
    # You can prune binaries using 'chmod u-s' and 'chmod g-s'

# Fix etc by making sure none of our config files got overwritten
    cd /etc
    svn status -q
    # Some usual candidates for clobbering include nsswitch.conf,
    # resolv.conf and sysconfig/openafs
    # [WIZARD/TEST] Remember that changes you made should not get
    # reverted!

# Reboot the machine to restore a consistent state, in case you
# changed anything. (Note: Starting kdump fails (this is ok))

# ------------------------------->8-------------------------------
#                ADDENDA AND MISCELLANEOUS THINGS

# [OPTIONAL] Your machine's hostname is baked in at install time;
# in the rare case you need to change it: it appears to be in:
#   o /etc/sysconfig/network
#   o your lvm thingies; probably don't need to edit

# [TESTSERVER] Enable password log in
        vim /etc/ssh/sshd_config
        service sshd reload
        vim /etc/pam.d/sshd
# Replace the first auth block with:
#           # If they're not root, but their user exists (success),
#           auth    [success=ignore ignore=ignore default=1]        pam_succeed_if.so uid > 0
#           # print the "You don't have tickets" error:
#           auth    [success=die ignore=reset default=die]  pam_echo.so file=/etc/issue.net.no_tkt
#           # If !(they are root),
#           auth    [success=1 ignore=ignore default=ignore]        pam_succeed_if.so uid eq 0
#           # print the "your account doesn't exist" error:
#           auth    [success=die ignore=reset default=die]  pam_echo.so file=/etc/issue.net.no_user


# [WIZARD/TESTSERVER] If you are setting up a non-production server,
# there are some services that it won't provide, and you will need to
# make it talk to a real server instead.  In particular:
#   - We don't serve the web, so don't bind scripts.mit.edu
#   - We don't serve LDAP, so use another server
# XXX: Someone should write sed scripts to do this
# This involves editing the following files:
        \rm /etc/sysconfig/network-scripts/ifcfg-lo:{0,1,2,3}
        \rm /etc/sysconfig/network-scripts/route-eth1 # [TESTSERVER] only
#   o /etc/nslcd.conf
#       replace: uri ldapi://%2fvar%2frun%2fdirsrv%2fslapd-scripts.socket/
#       with: uri ldap://scripts.mit.edu/
#           (what happened to nss-ldapd?)
#   o /etc/openldap/ldap.conf
#       add: URI ldap://scripts.mit.edu/
#            BASE dc=scripts,dc=mit,dc=edu
#   o /etc/httpd/conf.d/vhost_ldap.conf
#       replace: VhostLDAPUrl "ldap://127.0.0.1/ou=VirtualHosts,dc=scripts,dc=mit,dc=edu"
#       with: VhostLDAPUrl "ldap://scripts.mit.edu/ou=VirtualHosts,dc=scripts,dc=mit,dc=edu"
#   o /etc/postfix/virtual-alias-{domains,maps}-ldap.cf
#       replace: server_host ldapi://%2fvar%2frun%2fdirsrv%2fslapd-scripts.socket/
#       with: server_host = ldap://scripts.mit.edu
# to use scripts.mit.edu instead of localhost.

# [WIZARD/TESTSERVER] If you are setting up a non-production server,
# afsagent's cronjob will attempt to be renewing with the wrong
# credentials (daemon.scripts). Change this:
    vim /home/afsagent/renew # replace all mentions of daemon.scripts.mit.edu

# [TESTSERVER]
#   - You need a self-signed SSL cert or Apache will refuse to start
#     or do SSL.  Generate with:
    openssl req -new -x509 -keyout /etc/pki/tls/private/scripts.key -out /etc/pki/tls/certs/scripts.cert -nodes
    ln -s /etc/pki/tls/private/scripts.key /etc/pki/tls/private/scripts-1024.key
#     Also make /etc/pki/tls/certs/ca.pem match up
    openssl rsa -in /etc/pki/tls/private/scripts.key -pubout > /etc/pki/tls/certs/ca.pem

# [TESTSERVER] More stuff for test servers
#   - Make (/etc/aliases) root mail go to /dev/null, so we don't spam people
#   - Edit /etc/httpd/conf.d/scripts-vhost-names.conf to have scripts-fX-test.xvm.mit.edu
#     be an accepted vhost name
#   - Look at the old test server and see what config changes are floating around
