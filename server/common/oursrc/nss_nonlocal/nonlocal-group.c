/*
 * nonlocal-group.c
 * group database for nss_nonlocal proxy
 *
 * Copyright © 2007–2010 Anders Kaseorg <andersk@mit.edu> and Tim
 * Abbott <tabbott@mit.edu>
 *
 * This file is part of nss_nonlocal.
 *
 * nss_nonlocal is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2.1 of
 * the License, or (at your option) any later version.
 *
 * nss_nonlocal is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with nss_nonlocal; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
 * 02110-1301  USA
 */

#define _GNU_SOURCE

#include <sys/types.h>
#include <dlfcn.h>
#include <errno.h>
#include <grp.h>
#include <nss.h>
#include <pwd.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <unistd.h>

#include "nsswitch-internal.h"
#include "nonlocal.h"

/*
 * If the MAGIC_NONLOCAL_GROUPNAME local group exists, then nonlocal
 * users will be automatically added to it.  Furthermore, if a local
 * user is added to this group, then that user will inherit any
 * nonlocal gids from a nonlocal user of the same name, as
 * supplementary gids.
 */
#define MAGIC_NONLOCAL_GROUPNAME "nss-nonlocal-users"

/*
 * If the MAGIC_LOCAL_GROUPNAME local group exists, then local users
 * will be automatically added to it.
 */
#define MAGIC_LOCAL_GROUPNAME "nss-local-users"

/*
 * If the MAGIC_NONLOCAL_USERNAME local user is added to a local
 * group, then the local group will inherit the nonlocal membership of
 * a group of the same gid.
 */
#define MAGIC_NONLOCAL_USERNAME "nss-nonlocal-users"


enum nss_status
_nss_nonlocal_getgrnam_r(const char *name, struct group *grp,
			 char *buffer, size_t buflen, int *errnop);

enum nss_status
_nss_nonlocal_getgrgid_r(gid_t gid, struct group *grp,
			 char *buffer, size_t buflen, int *errnop);


static service_user *__nss_group_nonlocal_database;

static int
internal_function
__nss_group_nonlocal_lookup(service_user **ni, const char *fct_name,
			    void **fctp)
{
    if (__nss_group_nonlocal_database == NULL
	&& __nss_database_lookup("group_nonlocal", NULL, NULL,
				 &__nss_group_nonlocal_database) < 0)
	return -1;

    *ni = __nss_group_nonlocal_database;

    *fctp = __nss_lookup_function(*ni, fct_name);
    return 0;
}


enum nss_status
check_nonlocal_gid(const char *user, const char *group, gid_t gid, int *errnop)
{
    enum nss_status status;
    struct group gbuf;
    char *buf;
    size_t buflen = sysconf(_SC_GETGR_R_SIZE_MAX);
    const struct walk_nss w = {
	.lookup = &__nss_group_lookup, .fct_name = "getgrgid_r",
	.status = &status, .errnop = errnop, .buf = &buf, .buflen = &buflen
    };
    const __typeof__(&_nss_nonlocal_getgrgid_r) self = &_nss_nonlocal_getgrgid_r;
#define args (gid, &gbuf, buf, buflen, errnop)
#include "walk_nss.h"
#undef args

    if (status == NSS_STATUS_TRYAGAIN)
	return status;
    else if (status != NSS_STATUS_SUCCESS)
	return NSS_STATUS_SUCCESS;

    if (group == NULL || strcmp(gbuf.gr_name, group) == 0) {
	char *const *mem;
	for (mem = gbuf.gr_mem; *mem != NULL; mem++)
	    if (strcmp(*mem, MAGIC_NONLOCAL_USERNAME) == 0) {
		status = check_nonlocal_user(*mem, errnop);
		if (status == NSS_STATUS_TRYAGAIN) {
		    free(buf);
		    return status;
		} else if (status == NSS_STATUS_NOTFOUND) {
		    free(buf);
		    return NSS_STATUS_SUCCESS;
		}
		break;
	    }
    }

    syslog(LOG_DEBUG, "nss_nonlocal: removing local group %u (%s) from non-local user %s\n", gbuf.gr_gid, gbuf.gr_name, user);
    free(buf);
    return NSS_STATUS_NOTFOUND;
}

enum nss_status
check_nonlocal_group(const char *user, struct group *grp, int *errnop)
{
    enum nss_status status = NSS_STATUS_SUCCESS;
    int old_errno = errno;
    char *end;
    unsigned long gid;

    errno = 0;
    gid = strtoul(grp->gr_name, &end, 10);
    if (errno == 0 && *end == '\0' && (gid_t)gid == gid) {
	errno = old_errno;
	status = check_nonlocal_gid(user, grp->gr_name, gid, errnop);
    } else
	errno = old_errno;
    if (status != NSS_STATUS_SUCCESS)
	return status;

    return check_nonlocal_gid(user, grp->gr_name, grp->gr_gid, errnop);
}

enum nss_status
get_local_group(const char *name, struct group *grp, char **buffer, int *errnop)
{
    enum nss_status status;
    size_t buflen = sysconf(_SC_GETGR_R_SIZE_MAX);
    const struct walk_nss w = {
	.lookup = &__nss_group_lookup, .fct_name = "getgrnam_r",
	.status = &status, .errnop = errnop, .buf = buffer, .buflen = &buflen
    };
    const __typeof__(&_nss_nonlocal_getgrnam_r) self = &_nss_nonlocal_getgrnam_r;
#define args (name, grp, *buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    return status;
}

static bool grent_initialized = false;
static service_user *grent_startp, *grent_nip;
static void *grent_fct_start;
static union {
    enum nss_status (*l)(struct group *grp, char *buffer, size_t buflen,
			 int *errnop);
    void *ptr;
} grent_fct;
static const char *grent_fct_name = "getgrent_r";

enum nss_status
_nss_nonlocal_setgrent(int stayopen)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_group_nonlocal_lookup, .fct_name = "setgrent",
	.status = &status
    };
    const __typeof__(&_nss_nonlocal_setgrent) self = NULL;
#define args (stayopen)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (!grent_initialized) {
	__nss_group_nonlocal_lookup(&grent_startp, grent_fct_name,
				    &grent_fct_start);
	__sync_synchronize();
	grent_initialized = true;
    }
    grent_nip = grent_startp;
    grent_fct.ptr = grent_fct_start;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_endgrent(void)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_group_nonlocal_lookup, .fct_name = "endgrent",
	.status = &status, .all_values = 1,
    };
    const __typeof__(&_nss_nonlocal_endgrent) self = NULL;

    grent_nip = NULL;

#define args ()
#include "walk_nss.h"
#undef args
    return status;
}

enum nss_status
_nss_nonlocal_getgrent_r(struct group *grp, char *buffer, size_t buflen,
			 int *errnop)
{
    enum nss_status status;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    if (grent_nip == NULL) {
	status = _nss_nonlocal_setgrent(0);
	if (status != NSS_STATUS_SUCCESS)
	    return status;
    }
    do {
	if (grent_fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else {
	    int nonlocal_errno;
	    do
		status = DL_CALL_FCT(grent_fct.l, (grp, buffer, buflen, errnop));
	    while (status == NSS_STATUS_SUCCESS &&
		   check_nonlocal_group("(unknown)", grp, &nonlocal_errno) != NSS_STATUS_SUCCESS);
	}
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    return status;

	if (status == NSS_STATUS_SUCCESS)
	    return NSS_STATUS_SUCCESS;
    } while (__nss_next(&grent_nip, grent_fct_name, &grent_fct.ptr, status, 0) == 0);

    grent_nip = NULL;
    return NSS_STATUS_NOTFOUND;
}


enum nss_status
_nss_nonlocal_getgrnam_r(const char *name, struct group *grp,
			 char *buffer, size_t buflen, int *errnop)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_group_nonlocal_lookup, .fct_name = "getgrnam_r",
	.status = &status, .errnop = errnop
    };
    const __typeof__(&_nss_nonlocal_getgrnam_r) self = NULL;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

#define args (name, grp, buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (strcmp(name, grp->gr_name) != 0) {
	syslog(LOG_ERR, "nss_nonlocal: discarding group %s from lookup for group %s\n", grp->gr_name, name);
	return NSS_STATUS_NOTFOUND;
    }

    return check_nonlocal_group(name, grp, errnop);
}

enum nss_status
_nss_nonlocal_getgrgid_r(gid_t gid, struct group *grp,
			 char *buffer, size_t buflen, int *errnop)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_group_nonlocal_lookup, .fct_name = "getgrgid_r",
	.status = &status, .errnop = errnop
    };
    const __typeof__(&_nss_nonlocal_getgrgid_r) self = NULL;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

#define args (gid, grp, buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (gid != grp->gr_gid) {
	syslog(LOG_ERR, "nss_nonlocal: discarding gid %d from lookup for gid %d\n", grp->gr_gid, gid);
	return NSS_STATUS_NOTFOUND;
    }

    return check_nonlocal_group(grp->gr_name, grp, errnop);
}

static bool
add_group(gid_t group, long int *start, long int *size, gid_t **groupsp,
	  long int limit, int *errnop, enum nss_status *status)
{
    int i, old_errno = errno;
    for (i = 0; i < *start; ++i)
	if ((*groupsp)[i] == group)
	    return true;
    if (*start + 1 > *size) {
	gid_t *newgroups;
	long int newsize = 2 * *size;
	if (limit > 0) {
	    if (*size >= limit) {
		*status = NSS_STATUS_SUCCESS;
		return false;
	    }
	    if (newsize > limit)
		newsize = limit;
	}
	newgroups = realloc(*groupsp, newsize * sizeof((*groupsp)[0]));
	errno = old_errno;
	if (newgroups == NULL) {
	    *errnop = ENOMEM;
	    *status = NSS_STATUS_TRYAGAIN;
	    return false;
	}
	*groupsp = newgroups;
	*size = newsize;
    }
    (*groupsp)[(*start)++] = group;
    return true;
}

enum nss_status
_nss_nonlocal_initgroups_dyn(const char *user, gid_t group, long int *start,
			     long int *size, gid_t **groupsp, long int limit,
			     int *errnop)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_group_nonlocal_lookup, .fct_name = "initgroups_dyn",
	.status = &status, .all_values = 1, .errnop = errnop
    };
    const __typeof__(&_nss_nonlocal_initgroups_dyn) self = NULL;

    struct group local_users_group, nonlocal_users_group;
    bool is_nonlocal = true;
    char *buffer;
    int in, out, i;

    /* Check that the user is a nonlocal user, or a member of the
     * MAGIC_NONLOCAL_GROUPNAME group, before adding any groups. */
    status = check_nonlocal_user(user, errnop);
    if (status == NSS_STATUS_TRYAGAIN) {
	return status;
    } else if (status != NSS_STATUS_SUCCESS) {
	is_nonlocal = false;

	status = get_local_group(MAGIC_LOCAL_GROUPNAME,
				 &local_users_group, &buffer, errnop);
	if (status == NSS_STATUS_SUCCESS) {
	    free(buffer);
	    if (!add_group(local_users_group.gr_gid, start, size, groupsp,
			   limit, errnop, &status))
		return status;
	} else if (status == NSS_STATUS_TRYAGAIN) {
	    return status;
	} else {
	    syslog(LOG_WARNING,
		   "nss_nonlocal: Group %s does not exist locally!",
		   MAGIC_LOCAL_GROUPNAME);
	}
    }

    status = get_local_group(MAGIC_NONLOCAL_GROUPNAME,
			     &nonlocal_users_group, &buffer, errnop);
    if (status == NSS_STATUS_SUCCESS) {
	free(buffer);
	if (is_nonlocal) {
	    if (!add_group(nonlocal_users_group.gr_gid, start, size, groupsp,
			   limit, errnop, &status))
		return status;
	} else {
	    int i;
	    for (i = 0; i < *start; ++i) {
		if ((*groupsp)[i] == nonlocal_users_group.gr_gid) {
		    is_nonlocal = true;
		    break;
		}
	    }

	    if (is_nonlocal) {
		struct passwd pwbuf;
		char *buf;
		int nonlocal_errno = *errnop;
		status = get_nonlocal_passwd(user, &pwbuf, &buf, errnop);

		if (status == NSS_STATUS_SUCCESS) {
		    nonlocal_errno = *errnop;
		    status = check_nonlocal_gid(user, NULL, pwbuf.pw_gid,
						&nonlocal_errno);
		    free(buf);
		}

		if (status == NSS_STATUS_SUCCESS) {
		    if (!add_group(pwbuf.pw_gid, start, size, groupsp, limit,
				   errnop, &status))
			return status;
		} else if (status == NSS_STATUS_TRYAGAIN) {
		    *errnop = nonlocal_errno;
		    return status;
		}
	    }
	}
    } else if (status == NSS_STATUS_TRYAGAIN) {
	if (is_nonlocal)
	    return status;
    } else {
	syslog(LOG_WARNING, "nss_nonlocal: Group %s does not exist locally!",
	       MAGIC_NONLOCAL_GROUPNAME);
    }

    if (!is_nonlocal)
	return NSS_STATUS_SUCCESS;

    in = out = *start;

#define args (user, group, start, size, groupsp, limit, errnop)
#include "walk_nss.h"
#undef args
    if (status == NSS_STATUS_NOTFOUND || status == NSS_STATUS_UNAVAIL)
	return NSS_STATUS_SUCCESS;
    else if (status != NSS_STATUS_SUCCESS)
        return status;

    for (; in < *start; ++in) {
	int nonlocal_errno = *errnop;

	for (i = 0; i < out; ++i)
	    if ((*groupsp)[i] == (*groupsp)[in])
		break;
	if (i < out)
	    continue;

	status = check_nonlocal_gid(user, NULL, (*groupsp)[in],
				    &nonlocal_errno);
	if (status == NSS_STATUS_SUCCESS) {
	    (*groupsp)[out++] = (*groupsp)[in];
	} else if (status == NSS_STATUS_TRYAGAIN) {
	    *start = out;
	    *errnop = nonlocal_errno;
	    return status;
	}
    }

    *start = out;
    return NSS_STATUS_SUCCESS;
}
