# This document is a how-to for installing a Fedora scripts.mit.edu server.

set -e -x

[ -e /scripts-boot-count ] || echo 0 > /scripts-boot-count

source_server="old-faithful.mit.edu"

boot=${1:$(cat /scripts-boot-count)}

branch=branches/fc11-dev

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
    svn co svn://$source_server/$branch repository

    sed -i 's/^(# *)*store-passwords.*/store-passwords = no/' /root/.subversion/config
    sed -i 's/^(# *)*store-auth-creds.*/store-auth-creds = no/' /root/.subversion/config

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

# NOTE: You will have just lost DNS resolution and the abilit
# to do password SSH in

    service named start
    chkconfig named on

# XXX: This sometimes doesn't exist, but it really sucks if it
# does exist. So check for it.
# yum remove nss_ldap, because nss-ldapd conflicts with it

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
    rpm -i krb5-libs-1.6.3-20.fc11.i586.rpm
    rpm -U --force krb5-libs-1.6.3-20.fc11.scripts.1138.x86_64.rpm

# env NSS_NONLOCAL_IGNORE=1 yum install scripts-base
    YUM install -y scripts-base

# Install mit-zephyr
    YUM install -y mit-zephyr

# Remember to set NSS_NONLOCAL_IGNORE=1 anytime you're setting up
# anything, e.g. using yum. Otherwise useradd will query LDAP in a stupid way
# that makes it hang forever. (This is why we're using YUM, not yum)

# Reload the iptables config to take down the restrictive firewall 
    service iptables restart

# Copy over root's dotfiles from one of the other machines.
# Perhaps a useful change is to remove the default aliases

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
    echo "/afs:/usr/vice/cache:10000000" > /usr/vice/etc/cacheinfo
    # ezyang: ThisCell on b-k and c-w don't have anything special
    # written here

# Figure out why Zephyr isn't working. Most recently, it was because there
# was a 64-bit RPM installed; remove it and install Joe's 32-bit one
    YUM erase -y mit-zephyr
    # mit-zephyr has a spurious dependency on mit-krb-config
    yumdownloader mit-zephyr.i386
    # if deps change, this breaks
    YUM install -y libXaw.i586 libXext.i586 libXmu.i586 ncurses-libs.i586 readline.i58
    rpm -i --nodeps mit-zephyr-2.1-6-linux.i386.rpm

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

# ezyang: Running the below I got file conflicts. To fix (since I had
# botched steps above), I manually compared package lists and installed
# them.  If you've done the krb5 setup originally correctly, then
# write down what you had to do here.
    yumdownloader krb5-devel
    rpm -i --force krb5-devel-1.6.3-20.fc11.i586.rpm
    rpm -U --force krb5-devel-1.6.3-20.fc11.scripts.1138.x86_64.rpm
    yumdownloader krb5-server
    rpm -i --force krb5-server-1.6.3-20.fc11.scripts.1138.x86_64.rpm


# on another server, run:
rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > packages.txt
# arrange for packages.txt to be passed to the server, then run:
    # notice that yum is not capitalized
    # Also notice skip-broken
    NSS_NONLOCAL_IGNORE=1 cat packages.txt | xargs yum install -y --skip-broken

# Check which packages are installed on your new server that are not
# in the snapshot, and remove ones that aren't needed for some reason
# on the new machine.  Otherwise, aside from bloat, you may end up
# with undesirable things for security, like sendmail.
    rpm -qa --queryformat "%{Name}.%{Arch}\n" | sort > newpackages.txt
    diff -u packages.txt newpackages.txt  | less
    # if all went well, you'll probably see multiple kernel versions
    # as the only diff
    # ezyang: I got exim installed as another package

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
# - Look at `gem list` for Ruby gems.
#   Again, use 'yum search' and prefer RPMs, but failing that, 'gem install'.
#       ezyang: rspec-rails depends on rspec, and will override the Yum
#       package, so... don't use that RPM yet
# - Look at `pear list` for Pear fruits (or whatever they're called).
#   Yet again, 'yum search' for RPMs before resorting to 'pear install'.  Note
#   that for things in the beta repo, you'll need 'pear install package-beta'.
#   (you might get complaints about the php_scripts module; ignore them)
# - Look at `pecl list` for PECL things.  'yum search', and if you must,
#   'pecl install' needed items.
    # Automating this... will require a lot of batonning between
    # the servers. Probably best way to do it is to write an actual
    # script.

# Setup some Python config
    echo 'import site, os.path; site.addsitedir(os.path.expanduser("~/lib/python2.6/site-packages"))' > /usr/lib/python2.6/site-packages/00scripts-home.pth

# Build and install the scripts php module that enhances error logging info
# XXX This thing really ought to be packaged
    cp -r /srv/repository/server/common/oursrc/php_scripts /root
    cd /root/php_scripts
    ./build.sh
    cp test/modules/scripts.so /usr/lib64/php/modules

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
#       with: VhostLDAPUrl "ldap://18.181.0.46/ou=VirtualHosts,dc=scripts,dc=mit,dc=edu"
# to use scripts.mit.edu instead of localhost.
# XXX: someone should write sed scripts to do this

# If you are setting up a test server, afsagent's cronjob will attempt
# to be renewing with the wrong credentials (daemon.scripts). Change this:
    vim /home/afsagent/renew # replace all mentions of daemon.scripts.mit.edu

# Install fedora-ds-base and set up replication (see ./HOWTO-SETUP-LDAP
#   and ./fedora-ds-enable-ssl-and-kerberos.diff).

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

# Run fmtutil-sys --all, which does something that makes TeX work.
    fmtutil-sys --all
    # ezyang: I got errors on xetex

# Ensure that PHP isn't broken:
    mkdir /tmp/sessions
    chmod 01777 /tmp/sessions

# Ensure that fcgid isn't broken:
    chmod 755 /var/run/httpd
    chmod 755 /var/run/httpd/mod_fcgid
    # ezyang: The latter didn't exist for me

# Fix etc by making sure none of our config files got overwritten
    cd /etc
    svn status | grep M
    # ezyang: I had to revert krb5.conf, nsswitch.conf and sysconfig/openafs

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
#   o In the first install of not-backward, ThisCell got clobbered, resulting
#     in trying to get tickets from openafs.org. Not sure when it got
#     clobbered -- ezyang
#   o For some reason, syslog-ng wasn't turning on automatically, so we weren't
#     getting spew

# Some info about changing hostnames: it appears to be in:
#   o /etc/sysconfig/network
#   o your lvm thingies; probably don't need to edit
