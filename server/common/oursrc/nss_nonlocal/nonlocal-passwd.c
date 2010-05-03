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
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <dlfcn.h>
#include <stdio.h>
#include <syslog.h>
#include <errno.h>
#include <pwd.h>
#include <grp.h>
#include <nss.h>
#include "nsswitch-internal.h"
#include "nonlocal.h"


enum nss_status
_nss_nonlocal_getpwuid_r(uid_t uid, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop);
enum nss_status
_nss_nonlocal_getpwnam_r(const char *name, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop);


static service_user *
nss_passwd_nonlocal_database(void)
{
    static service_user *nip = NULL;
    if (nip == NULL)
	__nss_database_lookup("passwd_nonlocal", NULL, "", &nip);

    return nip;
}


enum nss_status
check_nonlocal_uid(const char *user, uid_t uid, int *errnop)
{
    static const char *fct_name = "getpwuid_r";
    static service_user *startp = NULL;
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(uid_t uid, struct passwd *pwd,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;
    struct passwd pwbuf;
    int old_errno = errno;

    size_t buflen = sysconf(_SC_GETPW_R_SIZE_MAX);
    char *buf = malloc(buflen);
    if (buf == NULL) {
	*errnop = ENOMEM;
	errno = old_errno;
	return NSS_STATUS_TRYAGAIN;
    }

    if (fct_start == NULL &&
	__nss_passwd_lookup(&startp, fct_name, &fct_start) != 0) {
	free(buf);
	return NSS_STATUS_UNAVAIL;
    }
    nip = startp;
    fct.ptr = fct_start;
    do {
    morebuf:
	if (fct.l == _nss_nonlocal_getpwuid_r)
	    status = NSS_STATUS_NOTFOUND;
	else
	    status = DL_CALL_FCT(fct.l, (uid, &pwbuf, buf, buflen, errnop));
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
	syslog(LOG_ERR, "nss_nonlocal: possible spoofing attack: non-local user %s has same UID as local user %s!\n", user, pwbuf.pw_name);
	status = NSS_STATUS_NOTFOUND;
    } else if (status != NSS_STATUS_TRYAGAIN) {
	status = NSS_STATUS_SUCCESS;
    }

    free(buf);
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
    if (errno == 0 && *end == '\0' && (uid_t)uid == uid)
	status = check_nonlocal_uid(user, uid, errnop);
    errno = old_errno;
    if (status != NSS_STATUS_SUCCESS)
	return status;

    return check_nonlocal_uid(user, pwd->pw_uid, errnop);
}

enum nss_status
check_nonlocal_user(const char *user, int *errnop)
{
    static const char *fct_name = "getpwnam_r";
    static service_user *startp = NULL;
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(const char *name, struct passwd *pwd,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;
    struct passwd pwbuf;
    int old_errno = errno;

    size_t buflen = sysconf(_SC_GETPW_R_SIZE_MAX);
    char *buf = malloc(buflen);
    if (buf == NULL) {
	*errnop = ENOMEM;
	errno = old_errno;
	return NSS_STATUS_TRYAGAIN;
    }

    if (fct_start == NULL &&
	__nss_passwd_lookup(&startp, fct_name, &fct_start) != 0) {
	free(buf);
	return NSS_STATUS_UNAVAIL;
    }
    nip = startp;
    fct.ptr = fct_start;
    do {
    morebuf:
	if (fct.l == _nss_nonlocal_getpwnam_r)
	    status = NSS_STATUS_NOTFOUND;
	else
	    status = DL_CALL_FCT(fct.l, (user, &pwbuf, buf, buflen, errnop));
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

    if (status == NSS_STATUS_SUCCESS)
	status = NSS_STATUS_NOTFOUND;
    else if (status != NSS_STATUS_TRYAGAIN)
	status = NSS_STATUS_SUCCESS;

    free(buf);
    return status;
}


static service_user *pwent_nip = NULL;
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
    static const char *fct_name = "setpwent";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(int stayopen);
	void *ptr;
    } fct;

    nip = nss_passwd_nonlocal_database();
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

    pwent_nip = nip;
    if (pwent_fct_start == NULL)
	pwent_fct_start = __nss_lookup_function(nip, pwent_fct_name);
    pwent_fct.ptr = pwent_fct_start;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_endpwent(void)
{
    static const char *fct_name = "endpwent";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(void);
	void *ptr;
    } fct;

    pwent_nip = NULL;

    nip = nss_passwd_nonlocal_database();
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
    static const char *fct_name = "getpwnam_r";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(const char *name, struct passwd *pwd,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;
    int group_errno;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    nip = nss_passwd_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;
    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, (name, pwd, buffer, buflen, errnop));
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    break;
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (strcmp(name, pwd->pw_name) != 0) {
	syslog(LOG_ERR, "nss_nonlocal: discarding user %s from lookup for user %s\n", pwd->pw_name, name);
	return NSS_STATUS_NOTFOUND;
    }

    status = check_nonlocal_passwd(name, pwd, errnop);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (check_nonlocal_gid(name, pwd->pw_gid, &group_errno) !=
	NSS_STATUS_SUCCESS)
	pwd->pw_gid = 65534 /* nogroup */;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_getpwuid_r(uid_t uid, struct passwd *pwd,
			 char *buffer, size_t buflen, int *errnop)
{
    static const char *fct_name = "getpwuid_r";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(uid_t uid, struct passwd *pwd,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;
    int group_errno;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    nip = nss_passwd_nonlocal_database();
    if (nip == NULL)
	return NSS_STATUS_UNAVAIL;
    if (fct_start == NULL)
	fct_start = __nss_lookup_function(nip, fct_name);
    fct.ptr = fct_start;
    do {
	if (fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(fct.l, (uid, pwd, buffer, buflen, errnop));
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    break;
    } while (__nss_next(&nip, fct_name, &fct.ptr, status, 0) == 0);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (uid != pwd->pw_uid) {
	syslog(LOG_ERR, "nss_nonlocal: discarding uid %d from lookup for uid %d\n", pwd->pw_uid, uid);
	return NSS_STATUS_NOTFOUND;
    }

    status = check_nonlocal_passwd(pwd->pw_name, pwd, errnop);
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (check_nonlocal_gid(pwd->pw_name, pwd->pw_gid, &group_errno) !=
	NSS_STATUS_SUCCESS)
	pwd->pw_gid = 65534 /* nogroup */;
    return NSS_STATUS_SUCCESS;
}
