/*
 * nonlocal-shadow.c
 * shadow database for nss_nonlocal proxy.
 *
 * Copyright © 2007 Anders Kaseorg <andersk@mit.edu>
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#define _GNU_SOURCE
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <dlfcn.h>
#include <stdio.h>
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
    return status;
}
