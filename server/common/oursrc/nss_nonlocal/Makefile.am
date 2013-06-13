lib_LTLIBRARIES = libnss_nonlocal.la
libnss_nonlocal_la_SOURCES = \
    nonlocal-passwd.c nonlocal-group.c nonlocal-shadow.c \
    nonlocal.h nsswitch-internal.h walk_nss.h
libnss_nonlocal_la_LDFLAGS = \
    -version-info 2:0:0 \
    -export-symbols-regex '^_nss_nonlocal_' \
    -no-undefined -Wl,-z,defs

install-exec-hook:
	rm -f $(DESTDIR)$(libdir)/libnss_nonlocal.so
	rm -f $(DESTDIR)$(libdir)/libnss_nonlocal.la

uninstall-local:
	rm -f $(DESTDIR)$(libdir)/libnss_nonlocal.so.*
