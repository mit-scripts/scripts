# This document is a how-to for installing a Fedora scripts.mit.edu server.

set -e -x

[ -e /scripts-boot-count ] || echo 0 > /scripts-boot-count

source_server="old-faithful.mit.edu"

boot=${1:$(cat /scripts-boot-count)}

# XXX: let 'branch' be the current svn branch you are on

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
    for i in NetworkManager avahi-daemon bluetooth cups isdn nfslock nfs pcscd restorecond rpcbind rpcgssd rpcidmapd sendmail; do
	chkconfig "$i" off
    done

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

    YUM install -y subversion

    cd /srv
    svn co svn://$source_server/$branch repository

    sed -i 's/^(# *)*store-passwords.*/store-passwords = no/' /root/.subversion/config
    sed -i 's/^(# *)*store-auth-creds.*/store-auth-creds = no/' /root/.subversion/config
# The same tweaks should be made on /home/scripts-build/.subversion/config
# once it exists (do something with svn as scripts-build)

    chown -R scripts-build /srv/repository

# cd to server/fedora in the svn repository.
    cd /srv/repository/server/fedora

# Run "make install-deps" to install various prereqs.  Nonstandard
# deps are in /mit/scripts/rpm.
    YUM install -y make
    make install-deps

# Install bind
    YUM install -y bind

# Check out the scripts /etc configuration
    cd /root
    svn co svn://scripts.mit.edu/$branch/server/fedora/config/etc etc
    # backslash to make us not use the alias
    \cp -a etc /

# NOTE: You will have just lost DNS resolution and the ability
# to do password SSH in.  If you managed to botch this step without
# having named setup, you can do a quick fix by frobbing /etc/resolv.conf
# with a non 127.0.0.1 address for the DNS server.  Be sure to revert it once
# you have named.

    service named start
    chkconfig named on

# In the case of the Kerberos libraries, you'll be told that
# there are conflicting files with the 64-bit versions of the packages,
# which we scriptsify.  You'll have to use --force to install those
# rpms despite the conflicts.  After doing that, you may want to
# install the corresponding 64-bit scriptsified versions again, just
# to be safe in case the 32-bit versions overwrite files that differ.
# When you try this, it will complain that you already have the same
# version installed; again, you'll need to use --force to do it anyway.

# We need yumdownloader to force some RPMs
    # XXX: This might be wrong. Sanity check what packages ou
    # have when done
    YUM install -y yum-utils
    yumdownloader krb5-libs
    # XXX: These version numbers are hardcoded, need some cli-fu to generalize
    rpm -i krb5-libs-*.i586.rpm
    rpm -U --force krb5-libs-*.scripts.1138.x86_64.rpm

# env NSS_NONLOCAL_IGNORE=1 yum install scripts-base
    YUM install -y scripts-base

# Remember to set NSS_NONLOCAL_IGNORE=1 anytime you're setting up
# anything, e.g. using yum. Otherwise useradd will query LDAP in a stupid way
# that makes it hang forever. (This is why we're using YUM, not yum)

# Reload the iptables config to take down the restrictive firewall 
    service iptables restart

# Copy over root's dotfiles from one of the other machines.
# Perhaps a useful change is to remove the default aliases
    # On 2009-07-01, the dotfiles to transfer where:
    #   .bashrc .ldapvirc (<- HAS PRIVILEDGED DATA)
    #   .screenrc .ssh (<- directory) .vimrc
    # Trying to scp from server to server won't work, as scp
    # will attempt to negotiate a server-to-server connection.
    # Instead, scp to your trusted machine as a temporary file,
    # and then push to the other server
    # You'll need some way to authenticate to the server, and since
    # password logins are disabled, you'll need some way of
    # temporarily giving yourself credentials.  On a test server,
    # reenabling password authentication is ok: frob /etc/pam.d/sshd
    # and reverse apply r1068.

# Replace rsyslog with syslog-ng by doing:
    rpm -e --nodeps rsyslog
    YUM install -y syslog-ng
    chkconfig syslog-ng on

# Install various dependencies of the scripts system, including
# glibc-devel.i586 (ezyang: already installed for me),
# python-twisted-core (ditto), mod_fcgid, nrpe, nagios-plugins-all.
    YUM install -y mod_fcgid
    YUM install -y nrpe
    YUM install -y nagios-plugins-all

# Disable NetworkManager with chkconfig NetworkManager off. Configure
# networking on the front end and back end, and the routing table to send
# traffic over the back end. Make sure that chkconfig reports "network" on, so
# that the network will still be configured at next boot.
# ezyang: For me, NetworkManager was not installed at this point, and
# we had already done the basic config for networking front end and
# back end (because I wanted ssh access, and not just conserver access)

# Fix the openafs /usr/vice/etc <-> /etc/openafs mapping by changing
#  /usr/vice/etc/cacheinfo to contain:
#       /afs:/usr/vice/cache:10000000
# Also fix ThisCell to contain athena.mit.edu in both directories
# WARNING: if you're installing a test server, this needs to be much
# smaller; the max filesize on XVM is 10GB.  Pick something like
# 500000
    echo "/afs:/usr/vice/cache:10000000" > /usr/vice/etc/cacheinfo
    # ezyang: ThisCell on b-k and c-w don't have anything special
    # written here
# If you're making a test server, some of the AFS parameters are
# kind of retarded (and if you're low on disk space, will actually
# exhaust our inodes).
# Edit the parameters in /etc/sysconfig/openafs

# Figure out why Zephyr isn't working. Most recently, it was because there
# was a 64-bit RPM installed; remove it and install Joe's 32-bit one
    YUM erase -y mit-zephyr
    # mit-zephyr has a spurious dependency on mit-krb-config
    yumdownloader mit-zephyr.i386
    # if deps change, this breaks
    YUM install -y libXaw.i586 libXext.i586 libXmu.i586 ncurses-libs.i586 readline.i586
    rpm -i --nodeps mit-zephyr-2.1-6-linux.i386.rpm
    # test if it worked by sending an un-authed message
    zwrite -d -c scripts -i test

# Install the athena-base, athena-lprng, and athena-lprng-misc RPMs
# from the Athena 9 build (these are present in our yum repo).  Note
# that you will have to use --nodeps for at least one of the lprng
# ones because it thinks it needs the Athena hesiod RPM.  It doesn't
# really.  Before doing this, run it without --nodeps and arrange to
# install the rest of the things it really does depend on.  This will
# include a bunch of 32-bit rpms; go ahead and install the .i586 versions
# of them.
    YUM install -y athena-base
    YUM install -y athena-lprng
    yumdownloader athena-lprng-misc
    # ezyang: I couldn't find any deps for this that existed in the repos
    # You might get a "find: `/usr/athena/info': No such file or directory"
    # error; this is fine
    rpm -i --nodeps athena-lprng-misc-9.4-0.i386.rpm

# Install the full list of RPMs that users expect to be on the
# scripts.mit.edu servers.

# on another server, run:
rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > packages.txt
# arrange for packages.txt to be passed to the server, then run:
    # notice that yum is not capitalized
    # Also notice skip-broken
    cat packages.txt | NSS_NONLOCAL_IGNORE=1 xargs yum install -y --skip-broken

# Check which packages are installed on your new server that are not
# in the snapshot, and remove ones that aren't needed for some reason
# on the new machine.  Otherwise, aside from bloat, you may end up
# with undesirable things for security, like sendmail.
    rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > newpackages.txt
    diff -u packages.txt newpackages.txt  | less
    # if all went well, you'll probably see multiple kernel versions
    # as the only diff
    # ezyang: I got exim installed as another package
    # here's a cute script that removes all extra packages
    diff -u packages.txt newpackages.txt  | grep '+' | cut -c2- | grep -v "@" | grep -v "++" | xargs yum erase -y

# Check out the scripts /usr/vice/etc configuration
    cd /root
    mkdir vice
    cd vice
    svn co svn://scripts.mit.edu/trunk/server/fedora/config/usr/vice/etc etc
    \cp -a etc /usr/vice

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
    export PERL_MM_USE_DEFAULT=1
    # XXX: Some interactive gobbeldygook
    cpan
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
#   easy-install.pth will tell you what was easy_installed.
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

# Install the credentials.  There are a lot of things to remember here:
#   o This will be different if you're setting up our build/update server.
#   o You probably installed the machine keytab long ago
    ls -l /etc/krb5.keytab
#   o Use ktutil to combine the host/scripts.mit.edu and
#     host/scripts-vhosts.mit.edu keys with host/this-server.mit.edu in
#     the keytab.  Do not use 'k5srvutil change' on the combined keytab
#     or you'll break the other servers. (real servers only)
#   o The daemon.scripts keytab
    ls -l /etc/daemon.keytab
#   o The SSL cert private key (real servers only)
#   o The LDAP password for the signup process (real servers only)
#   o The SQL password for the signup process (real servers only)
#   o The whoisd password (real servers only)
#   o The LDAP keytab for this server, which will be used later (real servers only)
#   o Replace the ssh host keys with the ones common to all scripts servers (real servers only)
#   o You'll install an LDAP certificate signed by the scripts CA later (real servers only)
#   o Make sure root's .k5login is correct
    cat /root/.k5login
#   o Make sure logview's .k5login is correct (real servers only)

# If you are setting up a test server, pay attention to
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

# If you are setting up a test server, afsagent's cronjob will attempt
# to be renewing with the wrong credentials (daemon.scripts). Change this:
    vim /home/afsagent/renew # replace all mentions of daemon.scripts.mit.edu

# Install 389-ds-base and set up replication (see ./HOWTO-SETUP-LDAP
#   and ./389-ds-enable-ssl-and-kerberos.diff).

# Make the services dirsrv, nslcd, nscd, postfix, and httpd start at
# boot. Run chkconfig to make sure the set of services to be run is
# correct.
    chkconfig dirsrv on
    chkconfig nslcd on
    chkconfig nscd on
    chkconfig postfix on
    chkconfig httpd on

# nrpe is required for nagios alerts
    chkconfig nrpe on

# Postfix doesn't actually deliver mail; fix this
    cd /etc/postfix
    postmap virtual

# Munin might not be monitoring packages that were installed after it
    munin-node-configure --suggest --shell | sh

# Run fmtutil-sys --all, which does something that makes TeX work.
    fmtutil-sys --all
    # ezyang: I got errors on xetex

# Ensure that PHP isn't broken:
    mkdir /tmp/sessions
    chmod 01777 /tmp/sessions

# Ensure fcgid isn't broken
    chmod 755 /var/run/mod_fcgid # ezyang: I suspect this is no longer necessary

# Fix etc by making sure none of our config files got overwritten
    cd /etc
    svn status | grep M
    # ezyang: I had to revert krb5.conf (not with latest), nsswitch.conf and sysconfig/openafs

# ThisCell got clobbered, replace it with athena.mit.edu
    echo "athena.mit.edu" > /usr/vice/etc/ThisCell

# Reboot the machine to restore a consistent state, in case you
# changed anything.
    # ezyang: When I rebooted, the following things happened:
    #   o Starting kdump failed (this is ok)
    #   o postfix mailbombed us
    #   o firstboot configuration screen popped up (ignored; manually will do
    #     chkconfig after the fact)

# (Optional) Beat your head against a wall.

# Possibly perform other steps that I've neglected to put in this
# document.
#   o For some reason, syslog-ng wasn't turning on automatically, so we weren't
#     getting spew

# Some info about changing hostnames: it appears to be in:
#   o /etc/sysconfig/network
#   o your lvm thingies; probably don't need to edit

# More stuff for test servers
#   - You need a self-signed SSL cert.  Generate with:
    openssl req -new -x509 -keyout /etc/pki/tls/private/scripts.key -out /etc/pki/tls/certs/scripts.cert -nodes
#     Also make /etc/pki/tls/certs/ca.pem match up
#   - Make (/etc/aliases) root mail go to /dev/null, so we don't spam people
#   - Edit /etc/httpd/conf.d/scripts-vhost-names.conf to have scripts-fX-test.xvm.mit.edu
#     be an accepted vhost name
#   - Look at the old test server and see what config changes are floating around
