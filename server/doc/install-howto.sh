# This document is a how-to for installing a Fedora scripts.mit.edu server.

set -e -x

[ -e /scripts-boot-count ] || echo 0 > /scripts-boot-count

source_server="old-faithful.mit.edu"

boot=${1:$(cat /scripts-boot-count)}

doreboot() {
    echo $(( $boot + 1 )) > /scripts-boot-count;
    shutdown -r now "Rebooting for step $(cat /scripts-boot-count)"
}

YUM() {
    NSS_NONLOCAL_IGNORE=1 yum "$@"
}

# Helper files for the install are located in server/fedora/config.

# Start with a normal install of Fedora.

if [ $boot = 0 ]; then
# When the initial configuration screen comes up, under "Firewall
# configuration", disable the firewall, and under "System services", leave
# enabled (as of Fedora 9) acpid, anacron, atd, cpuspeed, crond,
# firstboot, fuse, haldaemon, ip6tables, iptables, irqbalance,
# kerneloops, mdmonitor, messagebus, microcode_ctl, netfs, network, nscd, ntpd,
# sshd, udev-post, and nothing else.
    echo "--disabled" > /etc/sysconfig/system-config-firewall
    for i in NetworkManager avahi-daemon bluetooth cups isdn nfslock pcscd restorecond rpcbind rpcgssd rpcidmapd sendmail; do
	chkconfig "$i" off
    done

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

    YUM install -y subversion

    cd /srv
    svn co svn://$source_server/ repository

    sed -i 's/^(# *)*store-passwords.*/store-passwords = no/' /root/.subversion/config
    sed -i 's/^(# *)*store-auth-creds.*/store-auth-creds = no/' /root/.subversion/config

    chown -R scripts-build /srv/repository

# cd to server/fedora in the svn repository.
    cd /srv/repository/server/fedora

# Run "make install-deps" to install various prereqs.  Nonstandard
# deps are in /mit/scripts/rpm.
    make install-deps

# Install bind
    YUM install -y bind

# Check out the scripts /etc configuration
    cd /root
    svn co svn://scripts.mit.edu/server/fedora/config/etc etc
    \cp -a etc /

# yum remove nss_ldap, because nss-ldapd conflicts with it

# env NSS_NONLOCAL_IGNORE=1 yum install scripts-base
    YUM install -y scripts-base

# Rebuild mit-zephyr on a 32-bit machine, like the one at Joe's home.

# Remember to set NSS_NONLOCAL_IGNORE=1 anytime you're setting up
# anything, e.g. using yum. Otherwise useradd will query LDAP in a stupid way
# that makes it hang forever.

# Install and configure bind
# - env NSS_NONLOCAL_IGNORE=1 yum install bind
# - chkconfig named on
# - service named start

# Reload the iptables config to take down the restrictive firewall 
# service iptables restart

# Copy over root's dotfiles from one of the other machines.

# Replace rsyslog with syslog-ng by doing:
# # rpm -e --nodeps rsyslog
# # yum install syslog-ng

# Install various dependencies of the scripts system, including syslog-ng,
# glibc-devel.i586, python-twisted-core, mod_fcgid, nrpe, nagios-plugins-all.

# Disable NetworkManager with chkconfig NetworkManager off. Configure
# networking on the front end and back end, and the routing table to send
# traffic over the back end. Make sure that chkconfig reports "network" on, so
# that the network will still be configured at next boot.

# Fix the openafs /usr/vice/etc <-> /etc/openafs mapping by changing
#  /usr/vice/etc/cacheinfo to contain:
#       /afs:/usr/vice/cache:10000000
# Also fix ThisCell to contain athena.mit.edu in both directories

# Figure out why Zephyr isn't working. Most recently, it was because there
# was a 64-bit RPM installed; remove it and install Joe's 32-bit one

# Install the athena-base, athena-lprng, and athena-lprng-misc RPMs
# from the Athena 9 build (these are present in our yum repo).  Note
# that you will have to use --nodeps for at least one of the lprng
# ones because it thinks it needs the Athena hesiod RPM.  It doesn't
# really.  Before doing this, run it without --nodeps and arrange to
# install the rest of the things it really does depend on.  This will
# include a bunch of 32-bit rpms; go ahead and install the .i586 versions
# of them.  In the case of the Kerberos libraries, you'll be told that
# there are conflicting files with the 64-bit versions of the packages,
# which we scriptsify.  You'll have to use --force to install those
# rpms despite the conflicts.  After doing that, you may want to
# install the corresponding 64-bit scriptsified versions again, just
# to be safe in case the 32-bit versions overwrite files that differ.
# When you try this, it will complain that you already have the same
# version installed; again, you'll need to use --force to do it anyway.
# Yuck.

# Install the full list of RPMs that users expect to be on the
# scripts.mit.edu servers.  See server/doc/rpm and
# server/doc/rpm_snapshot.  (Note that this is only a snapshot, and not
# all packages may in fact be in use.)

# Check which packages are installed on your new server that are not
# in the snapshot, and remove ones that aren't needed for some reason
# on the new machine.  Otherwise, aside from bloat, you may end up
# with undesirable things for security, like sendmail.

# Install the full list of perl modules that users expect to be on the
# scripts.mit.edu servers.
# - export PERL_MM_USE_DEFAULT=1
# - Run 'cpan', accept the default configuration, and do 'o conf
#   prerequisites_policy follow'.
# - Parse the output of perldoc -u perllocal | grep head2 on an existing
#   server, and "notest install" them from the cpan prompt.
# TO DO THIS:
# On another server, run:
# perldoc -u perllocal | grep head2 | cut -f 3 -d '<' | cut -f 1 -d '|' | sort -u | perl -ne 'chomp; print "notest install $_\n" if system("rpm -q --whatprovides \"perl($_)\" >/dev/null 2>/dev/null")' > /mit/scripts/config/perl-packages.txt
# Then on the server you're installing,
#    cat perl-packages.txt | perl -MCPAN -e shell

# Install the Python eggs and Ruby gems and PEAR/PECL doohickeys that are on
# the other scripts.mit.edu servers and do not have RPMs.
# - Look at /usr/lib/python2.6/site-packages and
#           /usr/lib64/python2.6/site-packages for Python eggs and modules.
#   First use 'yum search' to see if the relevant package is now available
#   as an RPM, and install that if it is.  If not, then use easy_install.
# - Look at `gem list` for Ruby gems.
#   Again, use 'yum search' and prefer RPMs, but failing that, 'gem install'.
# - Look at `pear list` for Pear fruits (or whatever they're called).
#   Yet again, 'yum search' for RPMs before resorting to 'pear install'.  Note
#   that for things in the beta repo, you'll need 'pear install package-beta'.
# - Look at `pecl list` for PECL things.  'yum search', and if you must,
#   'pecl install' needed items.

# echo 'import site, os.path; site.addsitedir(os.path.expanduser("~/lib/python2.6/site-packages"))' > /usr/lib/python2.6/site-packages/00scripts-home.pth

# Build and install the scripts php module that enhances error logging info
# XXX This thing really ought to be packaged
# cp -r /srv/repository/server/common/oursrc/php_scripts /root
# cd /root/php_scripts
# ./build.sh
# cp test/modules/scripts.so /usr/lib64/php/modules

# Install the credentials.  There are a lot of things to remember here:
#   o You probably installed the machine keytab long ago
#   o Use ktutil to combine the host/scripts.mit.edu and
#     host/scripts-vhosts.mit.edu keys with host/this-server.mit.edu in
#     the keytab.  Do not use 'k5srvutil change' on the combined keytab
#     or you'll break the other servers.
#   o The daemon.scripts keytab
#   o The SSL cert private key
#   o The LDAP password for the signup process
#   o The SQL password for the signup process
#   o The LDAP keytab for this server, which will be used later
#   o Replace the ssh host keys with the ones common to all scripts servers
#   o You'll install an LDAP certificate signed by the scripts CA later
#   o Make sure root's .k5login is correct
#   o Make sure logview's .k5login is correct

# If you are setting up a test server, pay attention to
# /etc/sysconfig/network-scripts and do not bind scripts' IP address.
# You will also need to modify /etc/ldap.conf, /etc/nss-ldapd.conf,
# /etc/openldap/ldap.conf, and /etc/httpd/conf.d/vhost_ldap.conf to
# use scripts.mit.edu instead of localhost.

# Install fedora-ds-base and set up replication (see ./HOWTO-SETUP-LDAP
#   and ./fedora-ds-enable-ssl-and-kerberos.diff).

# Make the services dirsrv, nslcd, nscd, postfix, and httpd start at
# boot. Run chkconfig to make sure the set of services to be run is
# correct.

# cd /etc/postfix; postmap virtual
# Otherwise postfix will appear to work, but actually not deliver mail

# Run fmtutil-sys --all, which does something that makes TeX work.

# Ensure that PHP isn't broken:
# # mkdir /tmp/sessions
# # chmod 01777 /tmp/sessions

# Reboot the machine to restore a consistent state, in case you
# changed anything.

# (Optional) Beat your head against a wall.

# Possibly perform other steps that I've neglected to put in this
# document.
