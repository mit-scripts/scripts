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
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <dlfcn.h>
#include <stdio.h>
#include <syslog.h>
#include <errno.h>
#include <grp.h>
#include <nss.h>
#include "nsswitch-internal.h"
#include "nonlocal.h"

#define MAGIC_NONLOCAL_GROUPNAME "nss-nonlocal-users"
#define MAGIC_LOCAL_GROUPNAME "nss-local-users"


enum nss_status
_nss_nonlocal_getgrnam_r(const char *name, struct group *grp,
			 char *buffer, size_t buflen, int *errnop);

enum nss_status
_nss_nonlocal_getgrgid_r(gid_t gid, struct group *grp,
			 char *buffer, size_t buflen, int *errnop);


static service_user *
nss_group_nonlocal_database(void)
{
    static service_user *nip = NULL;
    if (nip == NULL)
	__nss_database_lookup("group_nonlocal", NULL, "", &nip);

    return nip;
}


enum nss_status
check_nonlocal_gid(const char *user, gid_t gid, int *errnop)
{
    static const char *fct_name = "getgrgid_r";
    static service_user *startp = NULL;
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(gid_t gid, struct group *grp,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;
    struct group gbuf;
    int old_errno = errno;

    size_t buflen = sysconf(_SC_GETGR_R_SIZE_MAX);
    char *buf = malloc(buflen);
    if (buf == NULL) {
	*errnop = ENOMEM;
	errno = old_errno;
	return NSS_STATUS_TRYAGAIN;
    }

    if (fct_start == NULL &&
	__nss_group_lookup(&startp, fct_name, &fct_start) != 0) {
	free(buf);
	return NSS_STATUS_UNAVAIL;
    }
    nip = startp;
    fct.ptr = fct_start;
    do {
    morebuf:
	if (fct.l == _nss_nonlocal_getgrgid_r)
	    status = NSS_STATUS_NOTFOUND;
	else
	    status = DL_CALL_FCT(fct.l, (gid, &gbuf, buf, buflen, errnop));
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE) {
	    free(buf);
	    buflen *= 2;
	    buf = malloc(buflen);
	    if (buf == NULL) {
		*errnop = ENOMEM;
		errno = old_errno;
		return NSS_STATUS_TRYAGAIN;
	    }
	    goto morebuf;
	}
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);

    if (status == NSS_STATUS_SUCCESS) {
	syslog(LOG_DEBUG, "nss_nonlocal: removing local group %u (%s) from non-local user %s\n", gbuf.gr_gid, gbuf.gr_name, user);
	status = NSS_STATUS_NOTFOUND;
    } else if (status != NSS_STATUS_TRYAGAIN) {
	status = NSS_STATUS_SUCCESS;
    }

    free(buf);
    return status;
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
    if (errno == 0 && *end == '\0' && (gid_t)gid == gid)
	status = check_nonlocal_gid(user, gid, errnop);
    errno = old_errno;
    if (status != NSS_STATUS_SUCCESS)
	return status;

    return check_nonlocal_gid(user, grp->gr_gid, errnop);
}

enum nss_status
get_local_group(const char *name, struct group *grp, char **buffer, int *errnop)
{
    static const char *fct_name = "getgrnam_r";
    static service_user *startp = NULL;
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(const char *name, struct group *grp,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;
    size_t buflen;
    int old_errno = errno;

    buflen = sysconf(_SC_GETGR_R_SIZE_MAX);
    *buffer = malloc(buflen);
    if (*buffer == NULL) {
	*errnop = ENOMEM;
	errno = old_errno;
	return NSS_STATUS_TRYAGAIN;
    }

    if (fct_start == NULL &&
	__nss_group_lookup(&startp, fct_name, &fct_start) != 0) {
	free(*buffer);
	*buffer = NULL;
	return NSS_STATUS_UNAVAIL;
    }
    nip = startp;
    fct.ptr = fct_start;
    do {
    morebuf:
	if (fct.l == _nss_nonlocal_getgrnam_r)
	    status = NSS_STATUS_NOTFOUND;
	else
	    status = DL_CALL_FCT(fct.l, (name, grp, *buffer, buflen, errnop));
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE) {
	    free(*buffer);
	    buflen *= 2;
	    *buffer = malloc(buflen);
	    if (*buffer == NULL) {
		*errnop = ENOMEM;
		errno = old_errno;
		return NSS_STATUS_TRYAGAIN;
	    }
	    goto morebuf;
	}
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);

    if (status != NSS_STATUS_SUCCESS) {
	free(*buffer);
	*buffer = NULL;
    }

    return status;
}

static service_user *grent_nip = NULL;
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
    static const char *fct_name = "setgrent";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(int stayopen);
	void *ptr;
    } fct;

    nip = nss_group_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;
    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, (stayopen));
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    grent_nip = nip;
    if (grent_fct_start == NULL)
	grent_fct_start = __nss_lookup_function(nip, grent_fct_name);
    grent_fct.ptr = grent_fct_start;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_endgrent(void)
{
    static const char *fct_name = "endgrent";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(void);
	void *ptr;
    } fct;

    grent_nip = NULL;

    nip = nss_group_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;
    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, ());
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
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
    static const char *fct_name = "getgrnam_r";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(const char *name, struct group *grp,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    nip = nss_group_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;
    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, (name, grp, buffer, buflen, errnop));
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    break;
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
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
    static const char *fct_name = "getgrgid_r";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(gid_t gid, struct group *grp,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    nip = nss_group_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;
    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, (gid, grp, buffer, buflen, errnop));
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    break;
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (gid != grp->gr_gid) {
	syslog(LOG_ERR, "nss_nonlocal: discarding gid %d from lookup for gid %d\n", grp->gr_gid, gid);
	return NSS_STATUS_NOTFOUND;
    }

    return check_nonlocal_group(grp->gr_name, grp, errnop);
}

enum nss_status
_nss_nonlocal_initgroups_dyn(const char *user, gid_t group, long int *start,
			     long int *size, gid_t **groupsp, long int limit,
			     int *errnop)
{
    static const char *fct_name = "initgroups_dyn";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(const char *user, gid_t group, long int *start,
			     long int *size, gid_t **groupsp, long int limit,
			     int *errnop);
	void *ptr;
    } fct;

    struct group local_users_group, nonlocal_users_group;
    gid_t local_users_gid, gid;
    int is_local = 0;
    char *buffer;
    int old_errno;
    int in, out, i;

    /* Check that the user is a nonlocal user before adding any groups. */
    status = check_nonlocal_user(user, errnop);
    if (status == NSS_STATUS_TRYAGAIN)
	return status;
    else if (status != NSS_STATUS_SUCCESS)
	is_local = 1;

    old_errno = errno;

    status = get_local_group(MAGIC_LOCAL_GROUPNAME,
			     &local_users_group, &buffer, errnop);
    if (status == NSS_STATUS_SUCCESS) {
	local_users_gid = local_users_group.gr_gid;
	free(buffer);
    } else if (status == NSS_STATUS_TRYAGAIN) {
	return status;
    } else {
	syslog(LOG_WARNING, "nss_nonlocal: Group %s does not exist locally!",
	       MAGIC_LOCAL_GROUPNAME);
	local_users_gid = -1;
    }

    if (is_local) {
	gid = local_users_gid;
    } else {
 	status = get_local_group(MAGIC_NONLOCAL_GROUPNAME,
				 &nonlocal_users_group, &buffer, errnop);
	if (status == NSS_STATUS_SUCCESS) {
	    gid = nonlocal_users_group.gr_gid;
	    free(buffer);
	} else if (status == NSS_STATUS_TRYAGAIN) {
	    return status;
	} else {
	    syslog(LOG_WARNING, "nss_nonlocal: Group %s does not exist locally!",
		   MAGIC_NONLOCAL_GROUPNAME);
	    gid = -1;
	}
    }

    if (gid != -1) {
	int i;
	for (i = 0; i < *start; ++i)
	    if ((*groupsp)[i] == gid)
		break;
	if (i >= *start) {
	    if (*start + 1 > *size) {
		gid_t *newgroups;
		long int newsize = 2 * *size;
		if (limit > 0) {
		    if (*size >= limit)
			return NSS_STATUS_SUCCESS;
		    if (newsize > limit)
			newsize = limit;
		}
		newgroups = realloc(*groupsp, newsize * sizeof((*groupsp)[0]));
		if (newgroups == NULL) {
		    *errnop = ENOMEM;
		    errno = old_errno;
		    return NSS_STATUS_TRYAGAIN;
		}
		*groupsp = newgroups;
		*size = newsize;
	    }
	    (*groupsp)[(*start)++] = gid;
	}
    }

    if (is_local)
	return NSS_STATUS_SUCCESS;

    in = out = *start;

    nip = nss_group_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;

    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, (user, group, start, size, groupsp, limit, errnop));
        if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
            break;
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
    if (status != NSS_STATUS_SUCCESS)
        return status;

    for (; in < *start; ++in) {
	int nonlocal_errno = *errnop;

	for (i = 0; i < out; ++i)
	    if ((*groupsp)[i] == (*groupsp)[in])
		break;
	if (i < out)
	    continue;

	/* Don't let users get into MAGIC_LOCAL_GROUPNAME from nonlocal reasons. */
	if (local_users_gid == (*groupsp)[in]) {
	    syslog(LOG_WARNING, "nss_nonlocal: Nonlocal user %s removed from special local users group %s",
		   user, MAGIC_LOCAL_GROUPNAME);
	    continue;
	}

	status = check_nonlocal_gid(user, (*groupsp)[in], &nonlocal_errno);
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
