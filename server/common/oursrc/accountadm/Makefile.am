bin_PROGRAMS = admof

admof_SOURCES = admof.c
admof_LDADD = @KRB5_LIBS@ @HEIMDAL_LIBS@ @PTHREAD_LIBS@
admof_CFLAGS = @KRB5_CFLAGS@

ssh-admof: admof
	@cp -p $< $@
CLEANFILES = ssh-admof

dist_bin_SCRIPTS = mbash cronload
dist_sbin_SCRIPTS = \
	get-homedirs \
	ldap-backup \
	signup-scripts-backend \
	ssh-admof \
	vhostadd \
	vhostedit
dist_sysconf_DATA = mbashrc
