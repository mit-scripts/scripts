AC_INIT([execsys], [1.0])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

PKG_PROG_PKG_CONFIG
AC_ARG_WITH([systemdsystemunitdir],
        AS_HELP_STRING([--with-systemdsystemunitdir=DIR], [Directory for systemd service files]),
        [], [with_systemdsystemunitdir=$($PKG_CONFIG --variable=systemdsystemunitdir systemd)])
AC_SUBST([systemdsystemunitdir], [$with_systemdsystemunitdir])
AM_CONDITIONAL(HAVE_SYSTEMD, [test -n "$with_systemdsystemunitdir"])

AC_SUBST([trusteddir], [/usr/libexec/scripts-trusted])

AC_CONFIG_FILES(Makefile)
AC_OUTPUT
