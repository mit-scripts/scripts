lib_LTLIBRARIES = libnss_nonlocal.la
libnss_nonlocal_la_SOURCES = \
    nonlocal-passwd.c nonlocal-group.c nonlocal-shadow.c \
    nonlocal.h nsswitch-internal.h
libnss_nonlocal_la_LDFLAGS = \
    -version-info 2:0:0 \
    -export-symbols-regex '^_nss_nonlocal_'

noinst_PROGRAMS = .linktest
_linktest_SOURCES =
_linktest_LDADD = libnss_nonlocal.la
_linktest_LDFLAGS = -nostdlib -entry=0

install-exec-hook:
	rm -f $(DESTDIR)$(libdir)/libnss_nonlocal.so
	rm -f $(DESTDIR)$(libdir)/libnss_nonlocal.la
