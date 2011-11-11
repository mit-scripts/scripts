import os
import optparse
import socket
import tempfile
import shutil
import errno
import csv

import shell

HOST = socket.gethostname()

# XXX test server and wizard server

# UIDs (sketchy):
#   signup 102
#   fedora-ds 103 (sketchy, not true for b-b)
#   logview 501 (really sketchy, since it's in the dynamic range)

# Works for passwd and group, but be careful! They're different things!
def lookup(filename):
    # Super-safe to assume and volume IDs (expensive to check)
    r = {
        'root': 0,
        'sql': 537704221,
    }
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=':', quoting=csv.QUOTE_NONE)
        for row in reader:
            r[row[0]] = int(row[2])
    return r

# Format here assumes that we always chmod $USER:$USER ...
# but note the latter refers to group...
COMMON_CREDS = [
    ('root', 0o600, 'root/.bashrc'),
    ('root', 0o600, 'root/.screenrc'),
    ('root', 0o600, 'root/.ssh/authorized_keys'),
    ('root', 0o600, 'root/.ssh/authorized_keys2'),
    ('root', 0o600, 'root/.vimrc'),
    ('root', 0o600, 'root/.k5login'),
    # punted /root/.ssh/known_hosts

    # XXX user must be created in Kickstart
    ('logview', 0o600, 'home/logview/.k5login'),
    ]

COMMON_PROD_CREDS = [ # important: no leading slashes!
    ('root', 0o600, 'root/.ldapvirc'),
    ('root', 0o600, 'etc/ssh/ssh_host_dsa_key'),
    ('root', 0o600, 'etc/ssh/ssh_host_key'),
    ('root', 0o600, 'etc/ssh/ssh_host_rsa_key'),
    ('root', 0o600, 'etc/pki/tls/private/scripts-1024.key'),
    ('root', 0o600, 'etc/pki/tls/private/scripts.key'),
    ('root', 0o600, 'etc/whoisd-password'),
    ('root', 0o600, 'etc/daemon.keytab'),

    ('root', 0o644, 'etc/ssh/ssh_host_dsa_key.pub'),
    ('root', 0o644, 'etc/ssh/ssh_host_key.pub'),
    ('root', 0o644, 'etc/ssh/ssh_host_rsa_key.pub'),

    ('sql', 0o600, 'etc/sql-mit-edu.cfg.php'),
    ('signup', 0o600, 'etc/signup-ldap-pw'),
    ]

MACHINE_PROD_CREDS = [
    # XXX NEED TO CHECK THAT THESE ARE SENSIBLE
    ('root', 0o600, 'etc/krb5.keytab'),
    ('fedora-ds', 0o600, 'etc/dirsrv/keytab')
    ]

def mkdir_p(path): # it's like mkdir -p
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else: raise

# XXX This code is kind of dangerous, because we are directly using the
# kernel modules to manipulate possibly untrusted disk images.  This
# means that if an attacker can corrupt the disk, and exploit a problem
# in the kernel vfs driver, he can escalate a guest root exploit
# to a host root exploit.  Ultimately we should use libguestfs
# which makes this attack harder to pull off, but at the time of writing
# squeeze didn't package libguestfs.
#
# We try to minimize attack surface by explicitly specifying the
# expected filesystem type.
class WithMount(object):
    """Context for running code with an extra mountpoint."""
    guest = None
    types = None # comma separated, like the mount argument -t
    mount = None
    dev = None
    def __init__(self, guest, types):
        self.guest = guest
        self.types = types
    def __enter__(self):
        self.dev = "/dev/%s/%s-root" % (HOST, self.guest)

        mapper_name = shell.eval("kpartx", "-l", self.dev).split()[0]
        shell.call("kpartx", "-a", self.dev)
        mapper = "/dev/mapper/%s" % mapper_name

        # this is why bracketing functions and hanging lambdas are a good idea
        try:
            self.mount = tempfile.mkdtemp("-%s" % self.guest, 'vm-', '/mnt') # no trailing slash
            try:
                shell.call("mount", "--types", self.types, mapper, self.mount)
            except:
                os.rmdir(self.mount)
                raise
        except:
            shell.call("kpartx", "-d", self.dev)
            raise

        return self.mount
    def __exit__(self, _type, _value, _traceback):
        shell.call("umount", self.mount)
        os.rmdir(self.mount)
        shell.call("kpartx", "-d", self.dev)

def main():
    usage = """usage: %prog [push|pull|pull-common] GUEST"""

    parser = optparse.OptionParser(usage)
    # ext3 will probably supported for a while yet and a pretty
    # reasonable thing to always try
    parser.add_option('-t', '--types', dest="types", default="ext4,ext3",
            help="filesystem type(s)")
    parser.add_option('--creds-dir', dest="creds_dir", default="/root/creds",
            help="directory to store/fetch credentials in")
    options, args = parser.parse_args()

    if not os.path.isdir(options.creds_dir):
        raise Exception("/root/creds does not exist") # XXX STRING
    # XXX check owned by root and appropriately chmodded

    os.umask(0o077) # overly restrictive

    if len(args) != 2:
        parser.print_help()
        raise Exception("Wrong number of arguments")

    command = args[0]
    guest   = args[1]

    with WithMount(guest, options.types) as tmp_mount:
        uid_lookup = lookup("%s/etc/passwd" % tmp_mount)
        gid_lookup = lookup("%s/etc/group" % tmp_mount)
        def push_files(files, type):
            for (usergroup, perms, f) in files:
                dest = "%s/%s" % (tmp_mount, f)
                mkdir_p(os.path.dirname(dest)) # useful for .ssh
                # assuming OK to overwrite
                # XXX we could compare the files before doing anything...
                shutil.copyfile("%s/%s/%s" % (options.creds_dir, type, f), dest)
                try:
                    os.chown(dest, uid_lookup[usergroup], gid_lookup[usergroup])
                    os.chmod(dest, perms)
                except:
                    # never ever leave un-chowned files lying around
                    os.unlink(dest)
                    raise
        def pull_files(files, type):
            for (_, _, f) in files:
                dest = "%s/%s/%s" % (options.creds_dir, type, f)
                mkdir_p(os.path.dirname(dest))
                # error if doesn't exist
                shutil.copyfile("%s/%s" % (tmp_mount, f), dest)

        if command == "push":
            push_files(COMMON_CREDS, 'common')
            push_files(COMMON_PROD_CREDS,  'common')
            push_files(MACHINE_PROD_CREDS, 'machine/%s' % guest)
        elif command == "pull":
            pull_files(MACHINE_PROD_CREDS, 'machine/%s' % guest)
        elif command == "pull-common":
            pull_files(COMMON_CREDS, 'common')
            pull_files(COMMON_PROD_CREDS,  'common')

if __name__ == "__main__":
    main()
