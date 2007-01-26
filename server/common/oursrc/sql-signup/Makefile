install:
	install -Dpm 644 sql-signup-capps ${DESTDIR}/etc/security/console.apps/sql-signup
	install -Dpm 644 sql-signup-pam ${DESTDIR}/etc/pam.d/sql-signup
	install -DpT sql-signup-sbin ${DESTDIR}/usr/sbin/sql-signup
	mkdir -p ${DESTDIR}/usr/bin
	ln -nfs /usr/bin/consolehelper ${DESTDIR}/usr/bin/sql-signup

clean:
	rm -f ${DESTDIR}/usr/bin/sql-signup
	rm -f ${DESTDIR}/usr/sbin/sql-signup
	rm -f ${DESTDIR}/etc/pam.d/sql-signup
	rm -f ${DESTDIR}/etc/security/console.apps/sql-signup
