/*
 * nsswitch_internal.h
 * Prototypes for some internal glibc functions that we use.  Shhh.
 */

#ifndef NSSWITCH_INTERNAL_H
#define NSSWITCH_INTERNAL_H

typedef struct service_user service_user;

extern int
__nss_next (service_user **ni, const char *fct_name, void **fctp, int status,
            int all_values);

extern int
__nss_database_lookup (const char *database,
		       const char *alternative_name,
		       const char *defconfig, service_user **ni);

extern int
__nss_configure_lookup (const char *dbname, const char *service_line);

extern void
*__nss_lookup_function (service_user *ni, const char *fct_name);

#endif /* NSSWITCH_INTERNAL_H */
