/*
 * nonlocal-passwd.c
 * passwd database for nss_nonlocal proxy.
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


enum nss_status
_nss_nonlocal_getpwuid_r(uid_t uid, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop);
enum nss_status
_nss_nonlocal_getpwnam_r(const char *name, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop);


static service_user *__nss_passwd_nonlocal_database;

static int
internal_function
__nss_passwd_nonlocal_lookup(service_user **ni, const char *fct_name,
			     void **fctp)
{
    if (__nss_passwd_nonlocal_database == NULL
	&& __nss_database_lookup("passwd_nonlocal", NULL, NULL,
				 &__nss_passwd_nonlocal_database) < 0)
	return -1;

    *ni = __nss_passwd_nonlocal_database;

    *fctp = __nss_lookup_function(*ni, fct_name);
    return 0;
}


enum nss_status
check_nonlocal_uid(const char *user, uid_t uid, int *errnop)
{
    enum nss_status status;
    struct passwd pwbuf;
    char *buf;
    size_t buflen = sysconf(_SC_GETPW_R_SIZE_MAX);
    const struct walk_nss w = {
	.lookup = &__nss_passwd_lookup, .fct_name = "getpwuid_r",
	.status = &status, .errnop = errnop, .buf = &buf, .buflen = &buflen
    };
    const __typeof__(&_nss_nonlocal_getpwuid_r) self = &_nss_nonlocal_getpwuid_r;
#define args (uid, &pwbuf, buf, buflen, errnop)
#include "walk_nss.h"
#undef args

    if (status == NSS_STATUS_SUCCESS) {
	syslog(LOG_ERR, "nss_nonlocal: possible spoofing attack: non-local user %s has same UID as local user %s!\n", user, pwbuf.pw_name);
	free(buf);
	status = NSS_STATUS_NOTFOUND;
    } else if (status != NSS_STATUS_TRYAGAIN) {
	status = NSS_STATUS_SUCCESS;
    }

    return status;
}

enum nss_status
check_nonlocal_passwd(const char *user, struct passwd *pwd, int *errnop)
{
    enum nss_status status = NSS_STATUS_SUCCESS;
    int old_errno = errno;
    char *end;
    unsigned long uid;

    errno = 0;
    uid = strtoul(pwd->pw_name, &end, 10);
    if (errno == 0 && *end == '\0' && (uid_t)uid == uid) {
	errno = old_errno;
	status = check_nonlocal_uid(user, uid, errnop);
    } else {
	errno = old_errno;
    }
    if (status != NSS_STATUS_SUCCESS)
	return status;

    return check_nonlocal_uid(user, pwd->pw_uid, errnop);
}

enum nss_status
check_nonlocal_user(const char *user, int *errnop)
{
    enum nss_status status;
    struct passwd pwbuf;
    char *buf;
    size_t buflen = sysconf(_SC_GETPW_R_SIZE_MAX);
    const struct walk_nss w = {
	.lookup = __nss_passwd_lookup, .fct_name = "getpwnam_r",
	.status = &status, .errnop = errnop, .buf = &buf, .buflen = &buflen
    };
    const __typeof__(&_nss_nonlocal_getpwnam_r) self = &_nss_nonlocal_getpwnam_r;
#define args (user, &pwbuf, buf, buflen, errnop)
#include "walk_nss.h"
#undef args

    if (status == NSS_STATUS_SUCCESS) {
	free(buf);
	status = NSS_STATUS_NOTFOUND;
    } else if (status != NSS_STATUS_TRYAGAIN) {
	status = NSS_STATUS_SUCCESS;
    }

    return status;
}

enum nss_status
get_nonlocal_passwd(const char *name, struct passwd *pwd, char **buffer,
		    int *errnop)
{
    enum nss_status status;
    size_t buflen = sysconf(_SC_GETPW_R_SIZE_MAX);
    const struct walk_nss w = {
	.lookup = __nss_passwd_nonlocal_lookup, .fct_name = "getpwnam_r",
	.status = &status, .errnop = errnop, .buf = buffer, .buflen = &buflen
    };
    const __typeof__(&_nss_nonlocal_getpwnam_r) self = NULL;
#define args (name, pwd, *buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    return status;
}


static bool pwent_initialized = false;
static service_user *pwent_startp, *pwent_nip;
static void *pwent_fct_start;
static union {
    enum nss_status (*l)(struct passwd *pwd, char *buffer, size_t buflen,
			 int *errnop);
    void *ptr;
} pwent_fct;
static const char *pwent_fct_name = "getpwent_r";

enum nss_status
_nss_nonlocal_setpwent(int stayopen)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_passwd_nonlocal_lookup, .fct_name = "setpwent",
	.status = &status
    };
    const __typeof__(&_nss_nonlocal_setpwent) self = NULL;
#define args (stayopen)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (!pwent_initialized) {
	__nss_passwd_nonlocal_lookup(&pwent_startp, pwent_fct_name,
				     &pwent_fct_start);
	__sync_synchronize();
	pwent_initialized = true;
    }
    pwent_nip = pwent_startp;
    pwent_fct.ptr = pwent_fct_start;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_endpwent(void)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_passwd_nonlocal_lookup, .fct_name = "endpwent",
	.status = &status, .all_values = 1,
    };
    const __typeof__(&_nss_nonlocal_endpwent) self = NULL;

    pwent_nip = NULL;

#define args ()
#include "walk_nss.h"
#undef args
    return status;
}

enum nss_status
_nss_nonlocal_getpwent_r(struct passwd *pwd, char *buffer, size_t buflen,
			 int *errnop)
{
    enum nss_status status;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    if (pwent_nip == NULL) {
	status = _nss_nonlocal_setpwent(0);
	if (status != NSS_STATUS_SUCCESS)
	    return status;
    }
    do {
	if (pwent_fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else {
	    int nonlocal_errno;
	    do
		status = DL_CALL_FCT(pwent_fct.l, (pwd, buffer, buflen, errnop));
	    while (status == NSS_STATUS_SUCCESS &&
		   check_nonlocal_passwd(pwd->pw_name, pwd, &nonlocal_errno) != NSS_STATUS_SUCCESS);
	}
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    return status;

	if (status == NSS_STATUS_SUCCESS)
	    return NSS_STATUS_SUCCESS;
    } while (__nss_next(&pwent_nip, pwent_fct_name, &pwent_fct.ptr, status, 0) == 0);

    pwent_nip = NULL;
    return NSS_STATUS_NOTFOUND;
}


enum nss_status
_nss_nonlocal_getpwnam_r(const char *name, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop)
{
    enum nss_status status;
    int group_errno;
    const struct walk_nss w = {
	.lookup = __nss_passwd_nonlocal_lookup, .fct_name = "getpwnam_r",
	.status = &status, .errnop = errnop
    };
    const __typeof__(&_nss_nonlocal_getpwnam_r) self = NULL;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

#define args (name, pwd, buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (strcmp(name, pwd->pw_name) != 0) {
	syslog(LOG_ERR, "nss_nonlocal: discarding user %s from lookup for user %s\n", pwd->pw_name, name);
	return NSS_STATUS_NOTFOUND;
    }

    status = check_nonlocal_passwd(name, pwd, errnop);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (check_nonlocal_gid(name, NULL, pwd->pw_gid, &group_errno) !=
	NSS_STATUS_SUCCESS)
	pwd->pw_gid = 65534 /* nogroup */;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_getpwuid_r(uid_t uid, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop)
{
    enum nss_status status;
    int group_errno;
    const struct walk_nss w = {
	.lookup = &__nss_passwd_nonlocal_lookup, .fct_name = "getpwuid_r",
	.status = &status, .errnop = errnop
    };
    const __typeof__(&_nss_nonlocal_getpwuid_r) self = NULL;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

#define args (uid, pwd, buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (uid != pwd->pw_uid) {
	syslog(LOG_ERR, "nss_nonlocal: discarding uid %d from lookup for uid %d\n", pwd->pw_uid, uid);
	return NSS_STATUS_NOTFOUND;
    }

    status = check_nonlocal_passwd(pwd->pw_name, pwd, errnop);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (check_nonlocal_gid(pwd->pw_name, NULL, pwd->pw_gid, &group_errno) !=
	NSS_STATUS_SUCCESS)
	pwd->pw_gid = 65534 /* nogroup */;
    return NSS_STATUS_SUCCESS;
}
