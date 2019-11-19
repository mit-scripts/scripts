/*
 * nsswitch_internal.h
 * Prototypes for some internal glibc functions that we use.  Shhh.
 */

#ifndef NSSWITCH_INTERNAL_H
#define NSSWITCH_INTERNAL_H

#include <features.h>
#include "config.h"

/* glibc/config.h.in */
#if __GLIBC_PREREQ(2, 27)
# define internal_function
#elif defined USE_REGPARMS && !defined PROF && !defined __BOUNDED_POINTERS__
# define internal_function __attribute__ ((regparm (3), stdcall))
#else
# define internal_function
#endif

/* glibc/nss/nsswitch.h */
typedef struct service_user service_user;

extern int __nss_next2 (service_user **ni, const char *fct_name,
			const char *fct2_name, void **fctp, int status,
			int all_values);
extern int __nss_database_lookup2 (const char *database,
				   const char *alternative_name,
				   const char *defconfig, service_user **ni);
extern void *__nss_lookup_function (service_user *ni, const char *fct_name);

/* glibc/nss/XXX-lookup.c */
extern int __nss_passwd_lookup2 (service_user **ni, const char *fct_name,
				 const char *fct2_name, void **fctp)
    internal_function;
extern int __nss_group_lookup2 (service_user **ni, const char *fct_name,
				const char *fct2_name, void **fctp)
    internal_function;

#endif /* NSSWITCH_INTERNAL_H */
