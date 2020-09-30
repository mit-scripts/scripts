#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([scripts-accountadm], [0.1], [scripts@mit.edu])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AM_MAINTAINER_MODE([enable])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_HEADERS([config.h])
AC_USE_SYSTEM_EXTENSIONS

# Checks for programs.
AC_PROG_CC
# automake 1.12 seems to require this, but automake 1.11 doesn't recognize it
m4_ifdef([AM_PROG_AR], [AM_PROG_AR])
AC_PROG_INSTALL

# Checks for libraries.
AC_CHECK_LIB([resolv], [res_mkquery], [], [
    AC_MSG_CHECKING([if res_mkquery is provided by libresolv with mangled symbols])
    save_LIBS="$LIBS"
    LIBS="-lresolv $LIBS"
    AC_TRY_LINK([#include <resolv.h>],
                [res_mkquery(0,NULL,0,0,NULL,0,NULL,NULL,0);], [
                    AC_DEFINE(HAVE_LIBRESOLV, [1], [Define if your libresolv provides res_mkquery.])
		    AC_MSG_RESULT(yes)], [
		    LIBS="$save_LIBS"
		    AC_MSG_RESULT(no)])])

AX_PTHREAD
# MIT KRB5 is used for actual linking and runtime
PKG_CHECK_MODULES([KRB5], [mit-krb5])
# But OpenAFS needs heimdal libraries to operate
PKG_CHECK_MODULES([HEIMDAL], [heimdal-krb5])
AC_CHECK_LIB([roken], [rk_asnprintf], [], [], [$HEIMDAL_LIBS])
AC_CHECK_LIB([hcrypto], [hc_RAND_bytes], [], [], [$HEIMDAL_LIBS])
AC_CHECK_LIB([afsrpc_pic], [rx_GetCall], [], [], [$PTHREAD_LIBS $HEIMDAL_LIBS])
AC_CHECK_LIB([afsauthent_pic], [afsconf_Open], [], [], [$PTHREAD_LIBS $HEIMDAL_LIBS])

# Checks for header files.
AC_CHECK_HEADERS([limits.h netinet/in.h string.h syslog.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_TYPE_SIZE_T
AC_TYPE_SSIZE_T

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([strcasecmp])

# For mbash
AC_PATH_PROG([bash_path], [bash])

# For signup-scripts-backend
AC_PATH_PROG([hesinfo_path], [hesinfo])
AC_PATH_PROG([ldapadd_path], [ldapadd])
AC_PATH_PROG([sudo_path], [sudo])

AC_CONFIG_FILES([Makefile signup-scripts-backend mbash])
AC_OUTPUT
