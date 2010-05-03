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
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <dlfcn.h>
#include <stdio.h>
#include <syslog.h>
#include <errno.h>
#include <shadow.h>
#include <nss.h>

#include "nsswitch-internal.h"
#include "nonlocal.h"


static service_user *
nss_shadow_nonlocal_database(void)
{
    static service_user *nip = NULL;
    if (nip == NULL)
        __nss_database_lookup("shadow_nonlocal", NULL, "", &nip);

    return nip;
}


static service_user *spent_nip = NULL;
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
    static const char *fct_name = "setspent";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(int stayopen);
	void *ptr;
    } fct;

    nip = nss_shadow_nonlocal_database();
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

    spent_nip = nip;
    if (spent_fct_start == NULL)
	spent_fct_start = __nss_lookup_function(nip, spent_fct_name);
    spent_fct.ptr = spent_fct_start;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_nonlocal_endspent(void)
{
    static const char *fct_name = "endspent";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(void);
	void *ptr;
    } fct;

    spent_nip = NULL;

    nip = nss_shadow_nonlocal_database();
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
_nss_nonlocal_getspent_r(struct spwd *pwd, char *buffer, size_t buflen,
			 int *errnop)
{
    enum nss_status status;
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
    static const char *fct_name = "getspnam_r";
    static void *fct_start = NULL;
    enum nss_status status;
    service_user *nip;
    union {
	enum nss_status (*l)(const char *name, struct spwd *pwd,
			     char *buffer, size_t buflen, int *errnop);
	void *ptr;
    } fct;

    nip = nss_shadow_nonlocal_database();
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

    if (strcmp(name, pwd->sp_namp) != 0) {
	syslog(LOG_ERR, "nss_nonlocal: discarding shadow %s from lookup for shadow %s\n", pwd->sp_namp, name);
	return NSS_STATUS_NOTFOUND;
    }

    return NSS_STATUS_SUCCESS;
}
