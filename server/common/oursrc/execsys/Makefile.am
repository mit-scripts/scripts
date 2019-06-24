if HAVE_SYSTEMD
systemdsystemunit_DATA = \
        execsys-binfmt.service \
	scripts-svn.socket \
	scripts-svn@.service \
	scripts-git.socket \
	scripts-git@.service \
	scripts-local-smtp.socket \
	scripts-local-smtp@.service
endif

dist_sbin_SCRIPTS = \
	ldapize.pl \
	svnproxy.pl \
	gitproxy.pl \
	local-smtp-proxy

dist_trusted_SCRIPTS = \
	svn \
	git
