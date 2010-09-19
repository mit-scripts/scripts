# This document is a how-to for installing a Fedora scripts.mit.edu server.

set -e -x

# Some commands should be run as the scripts-build user, not root.

alias asbuild="sudo -u scripts-build"

# Old versions of this install document advised setting
# NSS_NONLOCAL_IGNORE=1 anytime you're setting up anything, e.g. using
# yum, warning that useradd will query LDAP in a stupid way that makes
# it hang forever.  As of Fedora 13, this does not seem to be a problem,
# so it's been removed from the instructions.  If an install is hanging,
# though, try adding NSS_NONLOCAL_IGNORE.

[ -e /scripts-boot-count ] || echo 0 > /scripts-boot-count

# This is actually just "pick an active scripts server".  It can't be
# scripts.mit.edu because our networking config points that domain
# at localhost, and if our server is not setup at that point things
# will break.
source_server="cats-whiskers.mit.edu"

boot=${1:$(cat /scripts-boot-count)}

# XXX: let 'branch' be the current svn branch you are on.  You want to
# use trunk if your just installing a new server, and branches/fcXX-dev
# if your preparing a server on a new Fedora release.

doreboot() {
    echo $(( $boot + 1 )) > /scripts-boot-count;
    shutdown -r now "Rebooting for step $(cat /scripts-boot-count)"
}

# Helper files for the install are located in server/fedora/config.

# Start with a minimal install of Fedora.

# Take updates
    yum update

if [ $boot = 0 ]; then

echo "--disabled" > /etc/sysconfig/system-config-firewall

# Turn on network, so we can connect at boot
chkconfig network on

# Edit /etc/selinux/config so it has SELINUX=disabled and reboot.
    sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
    doreboot
fi

if [ $boot = 1 ]; then
# Create a scripts-build user account, and set up rpm to build in 
# $HOME by doing a 
# cp config/home/scripts-build/.rpmmacros /home/scripts-build/
# (If you just use the default setup, it will generate packages 
# in /usr/src/redhat.)
    adduser scripts-build

# Check out the scripts.mit.edu svn repository. Configure svn not to cache
# credentials.

    yum install -y subversion

    cd /srv
    # We must use an explicit source_server while setting up the Scripts
    # server, because once we load the Scripts /etc configuration,
    # scripts.mit.edu will start resolving to localhost and
    # updates/commits will stop working.  This will be switched to
    # scripts.mit.edu at the end of the install process.
    svn co svn://$source_server/$branch repository

    sed -i 's/^\(# *\)?store-passwords.*/store-passwords = no/' /root/.subversion/config
    sed -i 's/^\(# *\)?store-auth-creds.*/store-auth-creds = no/' /root/.subversion/config

    chown -R scripts-build /srv/repository

    asbuild svn up # generate the config file
    asbuild sed -i 's/^\(# *\)?store-passwords.*/store-passwords = no/' /home/scripts-build/.subversion/config
    asbuild sed -i 's/^\(# *\)?store-auth-creds.*/store-auth-creds = no/' /home/scripts-build/.subversion/config

# cd to server/fedora in the svn repository.
    cd /srv/repository/server/fedora

# Run "make install-deps" to install various prereqs.  Nonstandard
# deps are in /mit/scripts/rpm.
    yum install -y make
    make install-deps
    # You should pay close attention to the output of this command, and
    # note if packages you think should exist don't exist anymore.

# Get some packages necessary for OpenAFS
    yum install -y redhat-lsb
    yum install -y autofs

# Copy over root's dotfiles from one of the other machines.
# Perhaps a useful change is to remove the default aliases
    cd /root
    ls -l .bashrc
    ls -l .ldapvirc
    ls -l .screenrc
    ls -l .ssh
    ls -l .vimrc
    # Trying to scp from server to server won't work, as scp
    # will attempt to negotiate a server-to-server connection.
    # Instead, scp to your trusted machine as a temporary file,
    # and then push to the other server

# Add scripts-build to the group 'mock'
    usermod -a -G mock scripts-build

# Install bind
    yum install -y bind

# Check out the scripts /etc configuration
    cd /root
    svn co svn://$source_server/$branch/server/fedora/config/etc etc
    # backslash to make us not use the alias
    \cp -a etc /

# NOTE: You will have just lost DNS resolution and the ability
# to do password SSH in.  If you managed to botch this step without
# having named setup, you can do a quick fix by frobbing /etc/resolv.conf
# with a non 127.0.0.1 address for the DNS server.  Be sure to revert it once
# you have named.

# You can get password SSH back by editing /etc/ssh/sshd_config (allow
# password auth) and /etc/pam.d/sshd (comment out the first three auth
# lines).  However, you can also temporarily install krb5 and setup the
# keytabs and k5login to get Kerberized authentication.

    service named start
    chkconfig named on

# This is the point at which you should start updating scriptsified
# packages for a new Fedora release.  Consult 'upgrade-tips' for more
# information.

    yum install -y scripts-base

# Reload the iptables config to take down the restrictive firewall 
    service iptables restart

# Check that fs sysname is correct.  You should see, among others,
# 'amd64_fedoraX_scripts' (vary X) and 'scripts'. If it's not, you
# probably did a distro upgrade and should update /etc/sysconfig/openafs.
    fs sysname

# Replace rsyslog with syslog-ng by doing:
    rpm -e --nodeps rsyslog
    yum install -y syslog-ng
    chkconfig syslog-ng on

# Install various dependencies of the scripts system, including
# glibc-devel.i586 (ezyang: already installed for me),
# python-twisted-core (ditto), mod_fcgid, nrpe, nagios-plugins-all.
    yum install -y mod_fcgid
    yum install -y nrpe
    yum install -y nagios-plugins-all
    yum install -y fprintd-pam

# Fix the openafs /usr/vice/etc <-> /etc/openafs mapping.
    echo "/afs:/usr/vice/cache:10000000" > /usr/vice/etc/cacheinfo
    echo "athena.mit.edu" > /usr/vice/etc/ThisCell

# [TEST SERVER] If you're installing a test server, this needs to be
# much smaller; the max filesize on XVM is 10GB.  Pick something like
# 500000. Also, some of the AFS parameters are kind of retarded (and if
# you're low on disk space, will actually exhaust our inodes).  Edit
# these parameters in /etc/sysconfig/openafs

# Test that zephyr is working
    chkconfig zhm on
    service zhm start
    echo 'Test!' | zwrite -d -c scripts -i test

# Install the full list of RPMs that users expect to be on the
# scripts.mit.edu servers.
rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > packages.txt
# arrange for packages.txt to be passed to the server, then run:
# --skip-broken will (usually) prevent you from having to sit through
# several minutes of dependency resolution until it decides that
# it can't install /one/ package.
    cat packages.txt | xargs yum install -y --skip-broken

# Check which packages are installed on your new server that are not
# in the snapshot, and remove ones that aren't needed for some reason
# on the new machine.  Otherwise, aside from bloat, you may end up
# with undesirable things for security, like sendmail.
    rpm -qa --queryformat "%{Name}.%{Arch}\n" | grep -v kernel | sort > newpackages.txt
    diff -u packages.txt newpackages.txt | grep -v kernel | less
    # here's a cute script that removes all extra packages
    diff -u packages.txt newpackages.txt | grep -v kernel | grep '+' | cut -c2- | grep -v "@" | grep -v "++" | xargs yum erase -y

# We need an upstream version of cgi which we've packaged ourselves, but
# it doesn't work with the haskell-platform package which expects
# explicit versions.  So temporarily rpm -e the package, and then
# install it again after you install haskell-platform.  [Note: You
# probably won't need this in Fedora 15 or something, when the Haskell
# Platform gets updated.]
    rpm -e ghc-cgi-devel ghc-cgi
    yum install haskell-platform
    yumdownloader ghc-cgi
    yumdownloader ghc-cgi-devel
    rpm -i ghc-cgi*.rpm
    rpm -i ghc-cgi-devel*.rpm

# Check out the scripts /usr/vice/etc configuration
    cd /root
    mkdir vice
    cd vice
    svn co svn://scripts.mit.edu/$branch/server/fedora/config/usr/vice/etc etc
    \cp -a etc /usr/vice

# Install the full list of perl modules that users expect to be on the
# scripts.mit.edu servers.
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
# - Look at `gem list` for Ruby gems.
#   Again, use 'yum search' and prefer RPMs, but failing that, 'gem install'.
#       ezyang: rspec-rails depends on rspec, and will override the Yum
#       package, so... don't use that RPM yet
# - Look at `pear list` for Pear fruits (or whatever they're called).
#   Yet again, 'yum search' for RPMs before resorting to 'pear install'.  Note
#   that for things in the beta repo, you'll need 'pear install package-beta'.
#   (you might get complaints about the php_scripts module; ignore them)
# - Look at `pecl list` for PECL things.  'yum search', and if you must,
#   'pecl install' needed items. If it doesn't work, try 'pear install
#   pecl/foo' or 'pecl install foo-beta' or those two combined.
    # Automating this... will require a lot of batonning between
    # the servers. Probably best way to do it is to write an actual
    # script.

# Setup some Python config
    echo 'import site, os.path; site.addsitedir(os.path.expanduser("~/lib/python2.6/site-packages"))' > /usr/lib/python2.6/site-packages/00scripts-home.pth

# Install the credentials.  There are a lot of things to remember here.
# Be sure to make sure the permissions match up (ls -l on an existing
# server!).
#   o This will be different if you're setting up our build/update server.
#   o You probably installed the machine keytab long ago
    ls -l /etc/krb5.keytab
#     Use ktutil to combine the host/scripts.mit.edu and
#     host/scripts-vhosts.mit.edu keys with host/this-server.mit.edu in
#     the keytab.  Do not use 'k5srvutil change' on the combined keytab
#     or you'll break the other servers. (real servers only).  Be
#     careful about writing out the keytab: if you write it to an
#     existing file the keys will just get appended
#   o The daemon.scripts keytab
    ls -l /etc/daemon.keytab
#   o The SSL cert private key (real servers only)
    ls -l /etc/pki/tls/private/scripts.key
#   o The LDAP password for the signup process (real servers only)
    ls -l /etc/signup-ldap-pw
#   o The SQL password for the signup process (real servers only) (you
#     only need one, chown as sql user)
    ls -l /usr/local/etc/sql-mit-edu.cfg.php
    ls -l /etc/sql-mit-edu.cfg.php
#   o The whoisd password (real servers only)
    ls -l /etc/whoisd-password
#   o The LDAP keytab for this server, which will be used later (real
#     servers only).
    ls -l /etc/dirsrv/keytab
#   o Replace the ssh host keys with the ones common to all scripts servers (real servers only)
    ls -l /etc/ssh/*key*
#   o Make sure root's .k5login is correct
    cat /root/.k5login
#   o Make sure logview's .k5login is correct (real servers only)
    cat /home/logview/.k5login

# [TEST SERVER] If you are setting up a test server, pay attention to
# /etc/sysconfig/network-scripts and do not bind scripts' IP address.
# You will also need to modify:
#   o /etc/ldap.conf
#       add: host scripts.mit.edu
#   o /etc/nss-ldapd.conf
#       replace: uri *****
#       with: uri ldap://scripts.mit.edu/
#   o /etc/openldap/ldap.conf
#       add: URI ldap://scripts.mit.edu/
#            BASE dc=scripts,dc=mit,dc=edu
#   o /etc/httpd/conf.d/vhost_ldap.conf
#       replace: VhostLDAPUrl ****
#       with: VhostLDAPUrl "ldap://scripts.mit.edu/ou=VirtualHosts,dc=scripts,dc=mit,dc=edu"
#   o /etc/postfix/virtual-alias-{domains,maps}-ldap.cf
#       replace: server_host *****
#       with: server_host = ldap://scripts.mit.edu
# to use scripts.mit.edu instead of localhost.
# XXX: someone should write sed scripts to do this

# [TEST SERVER] If you are setting up a test server, afsagent's cronjob
# will attempt to be renewing with the wrong credentials
# (daemon.scripts). Change this:
    vim /home/afsagent/renew # replace all mentions of daemon.scripts.mit.edu

# Install 389-ds-base and set up replication (see ./install-ldap).
    yum install 389-ds-base
    # [complicated procedure here]

# Make the services dirsrv, nslcd, nscd, postfix, and httpd start at
# boot. Run chkconfig to make sure the set of services to be run is
# correct.
    chkconfig dirsrv on
    chkconfig nslcd on
    chkconfig nscd on
    chkconfig postfix on
    chkconfig httpd on

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

# Ensure fcgid isn't broken (should be 755)
    ls -l /var/run/mod_fcgid

# Fix etc by making sure none of our config files got overwritten
    cd /etc
    svn status -q
    # Some usual candidates for clobbering include nsswitch.conf and
    # sysconfig/openafs

# ThisCell got clobbered, replace it with athena.mit.edu
    echo "athena.mit.edu" > /usr/vice/etc/ThisCell

# Kill unnecessary services. (It's probably good form to look through
# `chkconfig | grep on` manually)
    for i in avahi-daemon isdn nfslock pcscd rpcbind rpcgssd rpcidmapd; do
        chkconfig "$i" off
    done

# Reboot the machine to restore a consistent state, in case you
# changed anything. (Note: Starting kdump fails (this is ok))

# [OPTIONAL] Your machine's hostname is baked in at install time;
# in the rare case you need to change it: it appears to be in:
#   o /etc/sysconfig/network
#   o your lvm thingies; probably don't need to edit

# [TEST SERVER] More stuff for test servers
#   - You need a self-signed SSL cert.  Generate with:
    openssl req -new -x509 -keyout /etc/pki/tls/private/scripts.key -out /etc/pki/tls/certs/scripts.cert -nodes
#     Also make /etc/pki/tls/certs/ca.pem match up
#   - Make (/etc/aliases) root mail go to /dev/null, so we don't spam people
#   - Edit /etc/httpd/conf.d/scripts-vhost-names.conf to have scripts-fX-test.xvm.mit.edu
#     be an accepted vhost name
#   - Look at the old test server and see what config changes are floating around

# XXX: our SVN checkout should be updated to use scripts.mit.edu
# (repository and etc) once serving actually works.
    cd /etc
    svn switch --relocate svn://$source_server/ svn://scripts.mit.edu/
    cd /usr/vice/etc
    svn switch --relocate svn://$source_server/ svn://scripts.mit.edu/
    cd /srv/repository
    asbuild svn switch --relocate svn://$source_server/ svn://scripts.mit.edu/
    asbuild svn up # verify scripts.mit.edu works
