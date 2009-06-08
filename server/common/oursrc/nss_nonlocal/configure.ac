AC_INIT([nss_nonlocal], [1.9], [andersk@mit.edu])
AC_CANONICAL_TARGET
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

AC_PREFIX_DEFAULT([/])
AC_DISABLE_STATIC
AC_PROG_CC
AC_PROG_INSTALL
AC_PROG_LIBTOOL

case "$target_cpu" in
    i386 | i486 | i586 | i686 | i786)
	AC_DEFINE([USE_REGPARMS], [],
	          [Define if the regparm attribute shall be used for local functions (gcc on ix86 only).])
 	;;
esac

AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
