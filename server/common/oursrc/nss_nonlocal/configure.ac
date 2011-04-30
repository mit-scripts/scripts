AC_INIT([nss_nonlocal], [2.0], [andersk@mit.edu])
AC_CANONICAL_TARGET
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])

AC_PREFIX_DEFAULT([/])
AC_DISABLE_STATIC
AC_PROG_CC
AC_PROG_INSTALL
AC_PROG_LIBTOOL

AC_HEADER_STDBOOL

case "$target_cpu" in
    i386 | i486 | i586 | i686 | i786)
	AC_DEFINE([USE_REGPARMS], [],
	          [Define if the regparm attribute shall be used for local functions (gcc on ix86 only).])
 	;;
esac

AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
