exec_prefix = /
libdir = $(exec_prefix)/lib

INSTALL = install
CC = gcc
CFLAGS = -O2 -Wall

ALL_CFLAGS = $(CFLAGS) -fPIC
ALL_LDFLAGS = $(LDFLAGS) -shared -Wl,-x

all: libnss_nonlocal.so.2 linktest

OBJS = nonlocal-passwd.o nonlocal-group.o nonlocal-shadow.o

libnss_nonlocal.so.2: $(OBJS) libnss_nonlocal.map
	$(CC) -o $@ $(ALL_LDFLAGS) -Wl,-soname,$@ -Wl,--version-script=libnss_nonlocal.map $(OBJS) $(LOADLIBES) $(LDLIBS)

%.o: %.c
	$(CC) -c $(ALL_CFLAGS) $(CPPFLAGS) $<

nonlocal-passwd.o: nonlocal-passwd.c nsswitch-internal.h nonlocal.h
nonlocal-group.o: nonlocal-group.c nsswitch-internal.h nonlocal.h
nonlocal-shadow.o: nonlocal-shadow.c nsswitch-internal.h nonlocal.h

linktest: libnss_nonlocal.so.2
	$(CC) $(LDFLAGS) -nostdlib -Wl,--entry=0 -o /dev/null $^

install: libnss_nonlocal.so.2
	$(INSTALL) -d $(DESTDIR)$(libdir)
	$(INSTALL) -m a+r,u+w $< $(DESTDIR)$(libdir)/

clean:
	rm -f *.so.* *.o

.PHONY: all linktest install clean
