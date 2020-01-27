import os
import optparse
import socket
import tempfile
import shutil
import errno
import csv

import shell

HOST = socket.gethostname()

PROD_GUESTS = frozenset([
    'bees-knees',
    'cats-whiskers',
    'busy-beaver',
    'pancake-bunny',
    'whole-enchilada',
    'real-mccoy',
    'old-faithful',
    'better-mousetrap',
    'shining-armor',
    'golden-egg',
    'miracle-cure',
    'lucky-star',
    ])
WIZARD_GUESTS = frozenset([
    'not-backward',
    ])

COMMON_CREDS = {}

# Format here assumes that we always chmod $USER:$USER,
# but note the latter refers to group...
#
# Important: no leading slashes!
COMMON_CREDS['all'] = [
    ('root', 0o600, 'root/.bashrc'),
    ('root', 0o600, 'root/.screenrc'),
    ('root', 0o600, 'root/.ssh/authorized_keys'),
    ('root', 0o600, 'root/.ssh/authorized_keys2'),
    ('root', 0o600, 'root/.vimrc'),
    ('root', 0o600, 'root/.k5login'),
    ]

COMMON_CREDS['prod'] = [
    ('root', 0o600, 'root/.ldapvirc'),
    ('root', 0o600, 'etc/ssh/ssh_host_dsa_key'),
    ('root', 0o600, 'etc/ssh/ssh_host_key'),
    ('root', 0o600, 'etc/ssh/ssh_host_rsa_key'),
    ('root', 0o600, 'etc/pki/tls/private/scripts-1024.key'),
    ('root', 0o600, 'etc/pki/tls/private/scripts.key'),
    ('afsagent', 0o600, 'etc/daemon.keytab'),

    ('root', 0o644, 'etc/ssh/ssh_host_dsa_key.pub'),
    ('root', 0o644, 'etc/ssh/ssh_host_key.pub'),
    ('root', 0o644, 'etc/ssh/ssh_host_rsa_key.pub'),

    ('sql', 0o600, 'etc/sql-mit-edu.cfg.php'), # technically doesn't have to be secret anymore
    ('sql', 0o600, 'etc/sql-password'),
    ('signup', 0o600, 'etc/signup-ldap-pw'),
    ('logview', 0o600, 'home/logview/.k5login'), # XXX user must be created in Kickstart
    ]

# note that these are duplicates with 'prod', but the difference
# is that the files DIFFER between wizard and prod
COMMON_CREDS['wizard'] = [
    ('root', 0o600, 'etc/ssh/ssh_host_dsa_key'),
    ('root', 0o600, 'etc/ssh/ssh_host_key'),
    ('root', 0o600, 'etc/ssh/ssh_host_rsa_key'),
    ('afsagent', 0o600, 'etc/daemon.keytab'),

    ('root', 0o644, 'etc/ssh/ssh_host_dsa_key.pub'),
    ('root', 0o644, 'etc/ssh/ssh_host_key.pub'),
    ('root', 0o644, 'etc/ssh/ssh_host_rsa_key.pub'),
    ]

MACHINE_CREDS = {}

MACHINE_CREDS['all'] = [
    # XXX NEED TO CHECK THAT THE CONTENTS ARE SENSIBLE
    ('root', 0o600, 'etc/krb5.keytab'),
    ]

MACHINE_CREDS['prod'] = [
    ('fedora-ds', 0o600, 'etc/dirsrv/keytab'),
    ]

MACHINE_CREDS['wizard'] = []

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

def drop_caches():
    with open("/proc/sys/vm/drop_caches", 'w') as f:
        f.write("1")

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
        drop_caches()
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
        drop_caches()

def main():
    usage = """usage: %prog [push|pull] [common|machine] GUEST"""

    parser = optparse.OptionParser(usage)
    # ext3 will probably supported for a while yet and a pretty
    # reasonable thing to always try
    parser.add_option('-t', '--types', dest="types", default="ext4,ext3",
            help="filesystem type(s)") # same arg as 'mount'
    parser.add_option('--creds-dir', dest="creds_dir", default="/root/creds",
            help="directory to store/fetch credentials in")
    options, args = parser.parse_args()

    if not os.path.isdir(options.creds_dir):
        raise Exception("%s does not exist" % options.creds_dir)
    # XXX check owned by root and appropriately chmodded

    os.umask(0o077) # overly restrictive

    if len(args) != 3:
        parser.print_help()
        raise Exception("Wrong number of arguments")

    command = args[0]
    files   = args[1]
    guest   = args[2]

    if guest in PROD_GUESTS:
        mode = 'prod'
    elif guest in WIZARD_GUESTS:
        mode = 'wizard'
    else:
        raise Exception("Unrecognized guest %s" % guest)

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

        # XXX ideally we should check these *before* we mount, but Python
        # makes that pretty annoying to do
        if command == "push":
            run = push_files
        elif command == "pull":
            run = pull_files
        else:
            raise Exception("Unknown command %s, valid values are 'push' and 'pull'" % command)

        if files == 'common':
            run(COMMON_CREDS['all'], 'all')
            run(COMMON_CREDS[mode], mode)
        elif files == 'machine':
            run(MACHINE_CREDS['all'], 'machine/%s' % guest)
            run(MACHINE_CREDS[mode], 'machine/%s' % guest)
        else:
            raise Exception("Unknown file set %s, valid values are 'common' and 'machine'" % files)

if __name__ == "__main__":
    main()
