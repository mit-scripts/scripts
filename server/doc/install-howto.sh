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
#   o Adding it to ansible/inventory.yml in either scripts-real or
#     scripts-real-test
#   o If this is a new distribution, set use_* to false in inventory.yml
#     since none of the scripts packages will be built yet
#   o Adding routing rules for the static IP in
#     /etc/sysconfig/network-scripts/route-eth1
#   o Adding the IP address to the hosts file (same hosts as for
#     scripts-vhost-names)
#   o Put the hostname information in LDAP so SVN and Git work
#   o Set up Nagios monitoring on sipb-noc for the host
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
# For example,
    remctl xvm-remote control $server install mirror=http://mirrors.mit.edu/fedora/linux/ dist=30 arch=x86_64 ks=https://raw.githubusercontent.com/mit-scripts/scripts/ansible-realserver/server/fedora/ks/kickstart.txt

# On vSphere, create a new virtual machine with 6 CPUs, 10GB RAM, two
# disks of 100GB and 8GB each, two network cards on VLAN486 and
# VLAN461, and a serial port.
# Upload an install image using the Datastore tab, and attach it to
# the VM using Edit Settings. Don't forget to check the "Connected" box.
# To boot, use an F30 boot ISO, press tab on "Install", delete "rhgb
# quiet" and add to the command line

    inst.ks=https://raw.githubusercontent.com/mit-scripts/scripts/ansible-realserver/server/fedora/ks/prod.txt ip=18.4.86.57::18.4.86.1:255.255.255.0:better-mousetrap.mit.edu:eth0:none nameserver=18.0.72.3 biosdevname=0 net.ifnames=0

# [TEST] You'll need to fix some config now.  See bottom of document.

# Check the configuration progress with
    systemctl status ansible-config-me
# You can tail the log with
    journalctl -f -u ansible-config-me
# If the configuration fails, figure out what happened and rerun it with
    systemctl start ansible-config-me

# This is the point at which you should start updating scriptsified
# packages for a new Fedora release.  Consult 'upgrade-tips' for more
# information.

    su scripts-build -
    cd /srv/repository/fedora/server && make all
    cp /var/lib/mock/fedora-*/result/*.rpm /home/scripts-build/mock-local/
    createrepo ~/mock-local/

# Copy the built packages and repo metadata to /mit/scripts/yum-repos/rpm-fcNN-testing/
# After building packages, rerun Ansible to install and configure them.
# Note that web.mit.edu caching means you have to wait several minutes
# after installing the packages for them to become available.

    rm /etc/ansible-config-done
    systemctl start ansible-config-me

#   # All types of servers will have an /etc/daemon.keytab file, however,
#   # different types of server will have different credentials in this
#   # keytab.
#   #   [PRODUCTION] daemon.scripts
#   #   [WIZARD]     daemon.scripts-security-upd
#   #   [TESTSERVER] daemon.scripts-test

# [PRODUCTION] Set up replication (see ./install-ldap).
# You'll need the LDAP keytab for this server: be sure to chown it
# fedora-ds after you create the fedora-ds user
    ls -l /etc/dirsrv/keytab
    cat install-ldap

# Note about OpenAFS: Check that fs sysname is correct.  You should see,
# among others, 'amd64_fedoraX_scripts' (vary X) and 'scripts'. If it's
# not, you probably did a distro upgrade and should update
# tokensys (server/common/oursrc/tokensys/scripts-afsagent-startup.in)
    fs sysname

# Run fmtutil-sys --all, which does something that makes TeX work.
# (Note: this errors on XeTeX which is ok.)
    fmtutil-sys --all

# Check for unwanted setuid/setgid binaries
    find / -xdev -not -perm -o=x -prune -o -type f -perm /ug=s -print | grep -Fxvf /etc/scripts/allowed-setugid.list
    find / -xdev -not -perm -o=x -prune -o -type f -print0 | xargs -0r /usr/sbin/getcap | cut -d' ' -f1 | grep -Fxvf /etc/scripts/allowed-filecaps.list
    # You can prune the first set of binaries using 'chmod u-s' and 'chmod g-s'
    # and remove capabilities using 'setcap -r'

# Reboot the machine to restore a consistent state, in case you
# changed anything. (Note: Starting kdump fails (this is ok))

# ------------------------------->8-------------------------------
#                ADDENDA AND MISCELLANEOUS THINGS

# [OPTIONAL] Your machine's hostname is baked in at install time;
# in the rare case you need to change it: it appears to be in:
#   o /etc/sysconfig/network
#   o your lvm thingies; probably don't need to edit

# [WIZARD/TESTSERVER] If you are setting up a non-production server,
# afsagent's cronjob will attempt to be renewing with the wrong
# credentials (daemon.scripts). Change this:
    vim /home/afsagent/renew # replace all mentions of daemon.scripts.mit.edu

# [TESTSERVER]
#   - You might need a self-signed SSL cert depending on what you need to do.
#     Generate with: (XXX recommended CN?)
    openssl req -new -x509 -sha256 -newkey rsa:2048 -keyout /etc/pki/tls/private/scripts.key -out /etc/pki/tls/certs/scripts-cert.pem -nodes -extensions v3_req
    ln -s /etc/pki/tls/private/scripts.key /etc/pki/tls/private/scripts-2048.key
#     Also make the various public keys match up
    openssl rsa -in /etc/pki/tls/private/scripts.key -pubout > /etc/pki/tls/certs/star.scripts.pem
    openssl rsa -in /etc/pki/tls/private/scripts.key -pubout > /etc/pki/tls/certs/scripts.pem
    openssl rsa -in /etc/pki/tls/private/scripts.key -pubout > /etc/pki/tls/certs/scripts-cert.pem
#     Nuke the CSRs since they will all mismatch
#     XXX alternate strategy replace all the pem's as above
    cd /etc/httpd/vhosts.d
    svn rm *.conf
