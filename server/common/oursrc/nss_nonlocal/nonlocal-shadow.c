/*
 * nonlocal-shadow.c
 * shadow database for nss_nonlocal proxy.
 *
 * Copyright © 2007–2010 Anders Kaseorg <andersk@mit.edu>
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
#include <shadow.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>

#include "nsswitch-internal.h"
#include "nonlocal.h"


static service_user *__nss_shadow_nonlocal_database;

static int
internal_function
__nss_shadow_nonlocal_lookup(service_user **ni, const char *fct_name,
			    void **fctp)
{
    if (__nss_shadow_nonlocal_database == NULL
	&& __nss_database_lookup("shadow_nonlocal", NULL, NULL,
				 &__nss_shadow_nonlocal_database) < 0)
	return -1;

    *ni = __nss_shadow_nonlocal_database;

    *fctp = __nss_lookup_function(*ni, fct_name);
    return 0;
}


static bool spent_initialized = false;
static service_user *spent_startp, *spent_nip;
static void *spent_fct_start;
static union {
    enum nss_status (*l)(struct spwd *pwd, char *buffer, size_t buflen,
			 int *errnop);
    void *ptr;
} spent_fct;
static const char *spent_fct_name = "getspent_r";

enum nss_status
_nss_nonlocal_setspent(int stayopen)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_shadow_nonlocal_lookup, .fct_name = "setspent",
	.status = &status
    };
    const __typeof__(&_nss_nonlocal_setspent) self = NULL;
#define args (stayopen)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (!spent_initialized) {
	__nss_shadow_nonlocal_lookup(&spent_startp, spent_fct_name,
				     &spent_fct_start);
	__sync_synchronize();
	spent_initialized = true;
    }
    spent_nip = spent_startp;
    spent_fct.ptr = spent_fct_start;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_endspent(void)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = &__nss_shadow_nonlocal_lookup, .fct_name = "endspent",
	.status = &status
    };
    const __typeof__(&_nss_nonlocal_endspent) self = NULL;

    spent_nip = NULL;

#define args ()
#include "walk_nss.h"
#undef args
    return status;
}

enum nss_status
_nss_nonlocal_getspent_r(struct spwd *pwd, char *buffer, size_t buflen,
			 int *errnop)
{
    enum nss_status status;

    char *nonlocal_ignore = getenv(NONLOCAL_IGNORE_ENV);
    if (nonlocal_ignore != NULL && nonlocal_ignore[0] != '\0')
	return NSS_STATUS_UNAVAIL;

    if (spent_nip == NULL) {
	status = _nss_nonlocal_setspent(0);
	if (status != NSS_STATUS_SUCCESS)
	    return status;
    }
    do {
	if (spent_fct.ptr == NULL)
	    status = NSS_STATUS_UNAVAIL;
	else
	    status = DL_CALL_FCT(spent_fct.l, (pwd, buffer, buflen, errnop));	
	if (status == NSS_STATUS_TRYAGAIN && *errnop == ERANGE)
	    return status;

	if (status == NSS_STATUS_SUCCESS)
	    return NSS_STATUS_SUCCESS;
    } while (__nss_next(&spent_nip, spent_fct_name, &spent_fct.ptr, status, 0) == 0);

    spent_nip = NULL;
    return NSS_STATUS_NOTFOUND;
}


enum nss_status
_nss_nonlocal_getspnam_r(const char *name, struct spwd *pwd,
			 char *buffer, size_t buflen, int *errnop)
{
    enum nss_status status;
    const struct walk_nss w = {
	.lookup = __nss_shadow_nonlocal_lookup, .fct_name = "getspnam_r",
	.status = &status, .errnop = errnop
    };
    const __typeof__(&_nss_nonlocal_getspnam_r) self = NULL;
#define args (name, pwd, buffer, buflen, errnop)
#include "walk_nss.h"
#undef args
    if (status != NSS_STATUS_SUCCESS)
	return status;

    if (strcmp(name, pwd->sp_namp) != 0) {
	syslog(LOG_ERR, "nss_nonlocal: discarding shadow %s from lookup for shadow %s\n", pwd->sp_namp, name);
	return NSS_STATUS_NOTFOUND;
    }

    return NSS_STATUS_SUCCESS;
}
