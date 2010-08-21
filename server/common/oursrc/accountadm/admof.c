/* admof
 * Version 2.0, released 2007-12-30
 * Anders Kaseorg <andersk@mit.edu>
 * replacing Perl version by Jeff Arnold <jbarnold@mit.edu>
 *
 * Usage:
 *   admof scripts andersk/root@ATHENA.MIT.EDU
 * Outputs "yes" and exits with status 33 if the given principal is an
 * administrator of the locker.
 *
 * Requires tokens (to authenticate/encrypt the connection to the
 * ptserver) unless -noauth is given.
 */

#include <stdio.h>
#include <limits.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <pwd.h>
#include <unistd.h>
#include <netinet/in.h>
#include <afs/vice.h>
#include <afs/venus.h>
#include <afs/ptclient.h>
#include <afs/ptuser.h>
#include <afs/prs_fs.h>
#include <afs/ptint.h>
#include <afs/cellconfig.h>
#include <afs/afsutil.h>
#include <krb5.h>
#include <kerberosIV/krb.h>
#include <stdbool.h>
#include <syslog.h>

extern int pioctl(char *, afs_int32, struct ViceIoctl *, afs_int32);

#define die(args...) do { fprintf(stderr, args); pr_End(); exit(1); } while(0)
#define _STR(x) #x
#define STR(x) _STR(x)

#define SYSADMINS "system:scripts-root"
#define SYSADMIN_CELL "athena.mit.edu"

static bool
ismember(const char *user, const char *group)
{
    int flag;
    if (pr_IsAMemberOf((char *)user, (char *)group, &flag) == 0)
	return flag;
    else
	return 0;
}

/* Parse an ACL of n entries, returning the rights for user. */
static int
parse_rights(int n, const char **p, const char *user)
{
    int rights = 0, *trights = malloc(n * sizeof(int)), i;
    namelist tnames = {.namelist_len = n,
		       .namelist_val = malloc(n * PR_MAXNAMELEN)};
    idlist tids = {.idlist_len = 0,
		   .idlist_val = NULL};

    if (trights == NULL || tnames.namelist_val == NULL)
	die("internal error: malloc failed: %m");

    for (i = 0; i < n; ++i) {
	int off;
	if (sscanf(*p, "%" STR(PR_MAXNAMELEN) "s %d\n%n",
		   tnames.namelist_val[i], &trights[i], &off) < 2)
	    die("internal error: can't parse output from pioctl\n");
	*p += off;
    }

    if (pr_NameToId(&tnames, &tids) != 0)
	die("internal error: pr_NameToId failed");
    if (tids.idlist_len < n)
	die("internal error: pr_NameToId did not return enough ids");

    for (i = 0; i < n; ++i) {
	if (~rights & trights[i] &&
	    (strcasecmp(tnames.namelist_val[i], user) == 0 ||
	     (tids.idlist_val[i] < 0 && ismember(user, tnames.namelist_val[i]))))
	    rights |= trights[i];
    }

    /* Note: this first free probably should be xdr_free in OpenAFS 1.5.
     * See commits b40b606 and f02f2e8 */
    free(tids.idlist_val);
    tids.idlist_val = NULL;
    free(tnames.namelist_val);
    free(trights);

    return rights;
}

int
main(int argc, const char *argv[])
{
    /* Get arguments. */
    const char *locker, *name;
    afs_int32 secLevel;

    if (argc == 3) {
	locker = argv[1];
	name = argv[2];
	secLevel = 3;
    } else if (argc == 4 && strcmp("-noauth", argv[1]) == 0) {
	locker = argv[2];
	name = argv[3];
	secLevel = 0;
    } else {
	die("Usage: %s [-noauth] LOCKER PRINCIPAL\n", argv[0]);
    }

    /* Convert the locker into a directory. */
    char dir[PATH_MAX];
    int n;
    struct passwd *pwd = getpwnam(locker);
    if (pwd != NULL)
	n = snprintf(dir, sizeof dir, "%s", pwd->pw_dir);
    else
	n = snprintf(dir, sizeof dir, "/mit/%s", locker);
    if (n < 0 || n >= sizeof dir)
	die("internal error\n");

    /* For non-AFS homedirs, read the .k5login file. */
    if (strncmp(dir, "/afs/", 5) != 0 && strncmp(dir, "/mit/", 5) != 0) {
	if (chdir(dir) != 0)
	    die("internal error: chdir: %m\n");
	FILE *fp = fopen(".k5login", "r");
	if (fp == NULL)
	    die("internal error: .k5login: %m\n");
	struct stat st;
	if (fstat(fileno(fp), &st) != 0)
	    die("internal error: fstat: %m\n");
	if (st.st_uid != pwd->pw_uid && st.st_uid != 0) {
	    fclose(fp);
	    die("internal error: bad .k5login permissions\n");
	}
	bool found = false;
	char *line = NULL;
	size_t len = 0;
	ssize_t read;
	while ((read = getline(&line, &len, fp)) != -1) {
	    if (read > 0 && line[read - 1] == '\n')
		line[read - 1] = '\0';
	    if (strcmp(name, line) == 0) {
		found = true;
		break;
	    }
	}
	if (line)
	    free(line);
	fclose(fp);
	if (found) {
	    printf("yes\n");
	    exit(33);
	} else {
	    printf("no\n");
	    exit(1);
	}
    }

    /* Get the locker's cell. */
    char cell[MAXCELLCHARS];
    struct ViceIoctl vi;
    vi.in = NULL;
    vi.in_size = 0;
    vi.out = cell;
    vi.out_size = sizeof cell;
    if (pioctl(dir, VIOC_FILE_CELL_NAME, &vi, 1) != 0)
	die("internal error: pioctl: %m\n");

    if (pr_Initialize(secLevel, (char *)AFSDIR_CLIENT_ETC_DIRPATH, cell) != 0)
	die("internal error: pr_Initialize failed\n");

    /* Get the cell configuration. */
    struct afsconf_dir *configdir = afsconf_Open(AFSDIR_CLIENT_ETC_DIRPATH);
    if (configdir == NULL)
	die("internal error: afsconf_Open failed\n");
    struct afsconf_cell cellconfig;
    if (afsconf_GetCellInfo(configdir, cell, NULL, &cellconfig) != 0)
	die("internal error: afsconf_GetCellInfo failed\n");
    afsconf_Close(configdir);

    /* Figure out the cell's realm. */
    krb5_context context;
    krb5_init_context(&context);

    char **realm_list;
    if (krb5_get_host_realm(context, cellconfig.hostName[0], &realm_list) != 0 ||
	realm_list[0] == NULL)
	die("internal error: krb5_get_host_realm failed");

    /* Convert the Kerberos 5 principal into a (Kerberos IV-style) AFS
       name, omitting the realm if it equals the cell's realm. */
    krb5_principal principal;
    if (krb5_parse_name(context, name, &principal) != 0)
	die("internal error: krb5_parse_name failed");
    char pname[ANAME_SZ], pinst[INST_SZ], prealm[REALM_SZ];
    if (krb5_524_conv_principal(context, principal, pname, pinst, prealm) != 0)
	die("internal error: krb5_524_conv_principal failed\n");
    char user[MAX(PR_MAXNAMELEN, MAX_K_NAME_SZ)];
    if (kname_unparse(user, pname, pinst,
		      strcmp(prealm, realm_list[0]) == 0 ? NULL : prealm) != 0)
	die("internal error: kname_unparse failed\n");

    krb5_free_principal(context, principal);
    krb5_free_host_realm(context, realm_list);
    krb5_free_context(context);

    /* Instead of canonicalizing the name as below, we just use
       strcasecmp above. */
#if 0
    afs_int32 id;
    if (pr_SNameToId((char *)user, &id) != 0)
	die("bad principal\n");
    if (id == ANONYMOUSID)
	die("anonymous\n");
    if (pr_SIdToName(id, user) != 0)
	die("internal error: pr_SIdToName failed\n");
#endif

    /* Read the locker ACL. */
    char acl[2048];
    vi.in = NULL;
    vi.in_size = 0;
    vi.out = acl;
    vi.out_size = sizeof acl;
    if (pioctl(dir, VIOCGETAL, &vi, 1) != 0)
	die("internal error: pioctl: %m\n");

    /* Parse the locker ACL to compute the user's rights. */
    const char *p = acl;

    int nplus, nminus;
    int off;
    if (sscanf(p, "%d\n%d\n%n", &nplus, &nminus, &off) < 2)
	die("internal error: can't parse output from pioctl\n");
    p += off;

    int rights = parse_rights(nplus, &p, user);
    rights &= ~parse_rights(nminus, &p, user);
    pr_End();

#ifdef SYSADMINS
    if (~rights & PRSFS_ADMINISTER) {
	strncpy(cell, SYSADMIN_CELL, MAXCELLCHARS - 1);
	if (pr_Initialize(secLevel, (char *)AFSDIR_CLIENT_ETC_DIRPATH, cell) == 0) {
	    if (ismember(user, SYSADMINS)) {
		openlog("admof", 0, LOG_AUTHPRIV);
		syslog(LOG_NOTICE, "giving %s admin rights on %s", user, locker);
		closelog();
		rights |= PRSFS_ADMINISTER;
	    }
	    pr_End();
	}
	/* If not, that's okay -- the normal codepath ran fine, so don't error */
    }
#endif

    /* Output whether the user is an administrator. */
    if (rights & PRSFS_ADMINISTER) {
	printf("yes\n");
	exit(33);
    } else {
	printf("no\n");
	exit(1);
    }
}
