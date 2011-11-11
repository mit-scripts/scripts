# This document is a how-to for installing a Fedora scripts.mit.edu server.
# It is semi-vaguely in the form of a shell script, but is not really
# runnable as it stands.

# Notation
# [PRODUCTION] Production server that will be put into the pool
# [WIZARD]     Semi-production server that will only have
#              daemon.scripts-security-upd bits, among other
#              restricted permissions
# [TESTSERVER] Completely untrusted server

# This is actually just "pick an active scripts server".  It can't be
# scripts.mit.edu because our networking config points that domain
# at localhost, and if our server is not setup at that point things
# will break.
source_server="shining-armor.mit.edu"

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
#      3    2      host/scripts.mit.edu@ATHENA.MIT.EDU
#
# The LDAP keytab should be by itself, so be sure to delete it and
# put it in its own file.

# ----------------------------->8--------------------------------------
#                      INFINITE INSTALLATION

# Start with a Scripts kickstarted install of Fedora (install-fedora)

# Take updates, reboot if there's a kernel update.
    yum update -y

# Get rid of network manager (XXX figure out to make kickstarter do
# this for us)
    yum remove NetworkManager

# Check out the scripts /etc configuration
    cd /root
    \cp -a etc /
    chmod 0440 /etc/sudoers

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
    svn revert resolv.conf hosts sysconfig/openafs

# Replace rsyslog with syslog-ng by doing:
    rpm -e --nodeps rsyslog
    yum install -y syslog-ng
    systemctl enable syslog-ng.service

# Install the full list of RPMs that users expect to be on the
# scripts.mit.edu servers.
rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > packages.txt
# arrange for packages.txt to be passed to the server, then run:
# --skip-broken will (usually) prevent you from having to sit through
# several minutes of dependency resolution until it decides that
# it can't install /one/ package.
    yum install -y --skip-broken $(cat packages.txt)

# Make sure sendmail isn't installed
    yum remove sendmail

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

# We need an upstream version of cgi which we've packaged ourselves, but
# it doesn't work with the haskell-platform package which expects
# explicit versions.  So temporarily rpm -e the package, and then
# install it again after you install haskell-platform.  [Note: You
# probably won't need this in Fedora 15 or something, when the Haskell
# Platform gets updated.]
    rpm -e ghc-cgi-devel ghc-cgi
    yum install -y haskell-platform
    yumdownloader ghc-cgi
    yumdownloader ghc-cgi-devel
    rpm -i ghc-cgi*1.8.1*.rpm

# ----------------------------->8--------------------------------------
#                      SPHEROID SHENANIGANS

# Note: Since ultimately we'd like to move away from using per-language
# package manager and all of these be RPMs, it is of questionable
# importance how much /good/ automation for these is necessary.

# Warning: For a new release, we're supposed to check if Fedora has
# packaged up the RPM.  Unfortunately we don't really have good incants
# for this.

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
    cat perl-packages.txt | perl -MCPAN -e shell

# Install the Python eggs and Ruby gems and PEAR/PECL doohickeys that are on
# the other scripts.mit.edu servers and do not have RPMs.
# The general mode of operation will be to run the "list" command
# on both servers, see what the differences are, check if those diffs
# are packaged up as rpms, and install them (rpm if possible, native otherwise)
# - Look at /usr/lib/python2.6/site-packages and
#           /usr/lib64/python2.6/site-packages for Python eggs and modules.
#   There will be a lot of gunk that was installed from packages;
#   easy-install.pth in /usr/lib/ will tell you what was easy_installed.
#   First use 'yum search' to see if the relevant package is now available
#   as an RPM, and install that if it is.  If not, then use easy_install.
#   Pass -Z to easy_install to install them unzipped, as some zipped eggs
#   want to be able to write to ~/.python-eggs.  (Also makes sourcediving
#   easier.)
# 'easy_install AuthKit jsonlib2 pygit'
cat /usr/lib/python2.7/site-packages/easy-install.pth | grep "^./" | cut -c3- | cut -f1 -d- > egg.txt
    cat egg.txt | xargs easy_install -Z

# - Look at `gem list` for Ruby gems.
#   Again, use 'yum search' and prefer RPMs, but failing that, 'gem install'.
#       ezyang: rspec-rails depends on rspec, and will override the Yum
#       package, so... don't use that RPM yet
# XXX This doesn't do the right thing for old version gems
gem list --no-version > gem.txt
    gem install $(gem list --no-version | grep -Fxvf - gem.txt)
    # Also, we need to install the old rails version

# - Look at `pear list` for Pear fruits (or whatever they're called).
#   Yet again, 'yum search' for RPMs before resorting to 'pear install'.  Note
#   that for things in the beta repo, you'll need 'pear install package-beta'.
#   (you might get complaints about the php_scripts module; ignore them)
pear list | tail -n +4 | cut -f 1 -d " " > pear.txt
    pear config-set preferred_state beta
    pear channel-update pear.php.net
    pear install $(pear list | tail -n +4 | cut -f 1 -d " " | grep -Fxvf - pear.txt)

# - Look at `pecl list` for PECL things.  'yum search', and if you must,
#   'pecl install' needed items. If it doesn't work, try 'pear install
#   pecl/foo' or 'pecl install foo-beta' or those two combined.
pecl list | tail -n +4 | cut -f 1 -d " " > pecl.txt
    pecl install --nodeps $(pecl list | tail -n +4 | cut -f 1 -d " " | grep -Fxvf - pecl.txt)

# ----------------------------->8--------------------------------------
#                       INFINITE CONFIGURATION

# Run credit-card to clone in credentials and make things runabble
python host.py push $server

# This is superseded by credit-card, but only for [PRODUCTION]
# Don't use credit-card on [WIZARD]: it will put in the wrong creds!
#
#   # All types of servers will have an /etc/daemon.keytab file, however,
#   # different types of server will have different credentials in this
#   # keytab.
#   #   [PRODUCTION] daemon.scripts
#   #   [WIZARD]     daemon.scripts-security-upd
#   #   [TESTSERVER] daemon.scripts-test

# [PRODUCTION/WIZARD] Fix the openafs /usr/vice/etc <-> /etc/openafs
# mapping.
    echo "/afs:/usr/vice/cache:10000000" > /usr/vice/etc/cacheinfo
    echo "athena.mit.edu" > /usr/vice/etc/ThisCell
# [TESTSERVER] If you're installing a test server, this needs to be
# much smaller; the max filesize on XVM is 10GB.  Pick something like
# 500000. Also, some of the AFS parameters are kind of retarded (and if
# you're low on disk space, will actually exhaust our inodes).  Edit
# these parameters in /etc/sysconfig/openafs (but wait, that won't
# work, will it...)
    echo "/afs:/usr/vice/cache:500000" > /usr/vice/etc/cacheinfo
    vim /etc/sysconfig/openafs

# Test that zephyr is working
    systemctl enable zhm.service
    systemctl start zhm.service
    echo 'Test!' | zwrite -d -c scripts -i test

# Check out the scripts /usr/vice/etc configuration
    cd /root/vice
    \cp -a etc /usr/vice

# [PRODUCTION] Set up replication (see ./install-ldap).
# You'll need the LDAP keytab for this server: be sure to chown it
# fedora-ds after you create the fedora-ds user
    ls -l /etc/dirsrv/keytab
    cat install-ldap

# Enable lots of services
    systemctl enable openafs-client.service
    systemctl enable dirsrv.service
    systemctl enable nslcd.service
    systemctl enable nscd.service
    systemctl enable postfix.service
    systemctl enable nrpe.service
    systemctl enable httpd.service # not for [WIZARD]

    systemctl start openafs-client.service
    systemctl start dirsrv.service
    systemctl start nslcd.service
    systemctl start nscd.service
    systemctl start postfix.service
    systemctl start nrpe.service
    systemctl start httpd.service # not for [WIZARD]

# Note about OpenAFS: Check that fs sysname is correct.  You should see,
# among others, 'amd64_fedoraX_scripts' (vary X) and 'scripts'. If it's
# not, you probably did a distro upgrade and should update
# /etc/sysconfig/openafs (XXX this is wrong: figuring out new
# systemd world order).
    fs sysname

# Postfix doesn't actually deliver mail; fix this
    cd /etc/postfix
    postmap virtual

# Munin might not be monitoring packages that were installed after it
    munin-node-configure --suggest --shell | sh

# Run fmtutil-sys --all, which does something that makes TeX work.
# (Note: this errors on XeTeX which is ok.)
    fmtutil-sys --all

# Ensure that PHP isn't broken:
    mkdir /tmp/sessions
    chmod 01777 /tmp/sessions
    # XXX: this seems to get deleted if tmp gets cleaned up, so we
    # might need something a little better (maybe init script.)

# Fix etc by making sure none of our config files got overwritten
    cd /etc
    svn status -q
    # Some usual candidates for clobbering include nsswitch.conf and
    # sysconfig/openafs
    # [WIZARD/TEST] Remember that changes you made should not get
    # reverted!

# ThisCell got clobbered, replace it with athena.mit.edu
    echo "athena.mit.edu" > /usr/vice/etc/ThisCell

# Reboot the machine to restore a consistent state, in case you
# changed anything. (Note: Starting kdump fails (this is ok))

# When all is said and done, fix up the Subversion checkouts
    cd /etc
    svn switch --relocate svn://$source_server/ svn://scripts.mit.edu/
    cd /usr/vice/etc
    svn switch --relocate svn://$source_server/ svn://scripts.mit.edu/
    cd /srv/repository
    # Some commands should be run as the scripts-build user, not root.
    alias asbuild="sudo -u scripts-build"
    asbuild svn switch --relocate svn://$source_server/ svn://scripts.mit.edu/
    asbuild svn up # verify scripts.mit.edu works

# ------------------------------->8-------------------------------
#                ADDENDA AND MISCELLANEOUS THINGS

# [OPTIONAL] Your machine's hostname is baked in at install time;
# in the rare case you need to change it: it appears to be in:
#   o /etc/sysconfig/network
#   o your lvm thingies; probably don't need to edit

# [WIZARD/TESTSERVER] If you are setting up a non-production server,
# there are some services that it won't provide, and you will need to
# make it talk to a real server instead.  In particular:
#   - We don't serve the web, so don't bind scripts.mit.edu
#   - We don't serve LDAP, so use another server
# This involves editing the following files:
#   o /etc/sysconfig/network-scripts/ifcfg-lo:0
#   o /etc/sysconfig/network-scripts/ifcfg-lo:1
#   o /etc/sysconfig/network-scripts/ifcfg-lo:2
#   o /etc/sysconfig/network-scripts/ifcfg-lo:3
       \rm /etc/sysconfig/network-scripts/ifcfg-lo:{0,1,2,3}
#   o /etc/ldap.conf
#       add: host scripts.mit.edu
#   o /etc/{nss-ldapd,nslcd}.conf
#       replace: uri ldapi://%2fvar%2frun%2fdirsrv%2fslapd-scripts.socket/
#       with: uri ldap://scripts.mit.edu/
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
# XXX: someone should write sed scripts to do this

# [WIZARD/TESTSERVER] If you are setting up a non-production server,
# afsagent's cronjob will attempt to be renewing with the wrong
# credentials (daemon.scripts). Change this:
    vim /home/afsagent/renew # replace all mentions of daemon.scripts.mit.edu

# [TESTERVER]
#   - You need a self-signed SSL cert or Apache will refuse to start
#     or do SSL.  Generate with:
    openssl req -new -x509 -keyout /etc/pki/tls/private/scripts.key -out /etc/pki/tls/certs/scripts.cert -nodes
#     Also make /etc/pki/tls/certs/ca.pem match up (XXX what's the
#     incant for that?)

# [TESTSERVER] More stuff for test servers
#   - Make (/etc/aliases) root mail go to /dev/null, so we don't spam people
#   - Edit /etc/httpd/conf.d/scripts-vhost-names.conf to have scripts-fX-test.xvm.mit.edu
#     be an accepted vhost name
#   - Look at the old test server and see what config changes are floating around
