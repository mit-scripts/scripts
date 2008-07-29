#ifndef NONLOCAL_H
#define NONLOCAL_H

#include "config.h"

enum nss_status check_nonlocal_uid(const char *user, uid_t uid, int *errnop);
enum nss_status check_nonlocal_gid(const char *user, gid_t gid, int *errnop);
enum nss_status check_nonlocal_user(const char *user, int *errnop);

#define NONLOCAL_IGNORE_ENV "NSS_NONLOCAL_IGNORE"

#endif /* NON_LOCAL_H */
