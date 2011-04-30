{
    static service_user *startp = NULL;
    static void *fct_start = NULL;

    service_user *nip;
    union {
	__typeof__(self) l;
	void *ptr;
    } fct;
    int old_errno = errno;

    if (fct_start == NULL &&
	w.lookup(&startp, w.fct_name, &fct_start) != 0) {
	*w.status = NSS_STATUS_UNAVAIL;
	goto walk_nss_out;
    }

    nip = startp;
    fct.ptr = fct_start;

    if (w.buf != NULL) {
	*w.buf = malloc(*w.buflen);
	errno = old_errno;
	if (*w.buf == NULL) {
	    *w.status = NSS_STATUS_TRYAGAIN;
	    *w.errnop = ENOMEM;
	    goto walk_nss_out;
	}
    }

    do {
    walk_nss_morebuf:
	if (fct.ptr == NULL)
	    *w.status = NSS_STATUS_UNAVAIL;
	else if (self != NULL && fct.l == self)
	    *w.status = NSS_STATUS_NOTFOUND;
	else
	    *w.status = DL_CALL_FCT(fct.l, args);
	if (*w.status == NSS_STATUS_TRYAGAIN &&
	    w.errnop != NULL && *w.errnop == ERANGE) {
	    if (w.buf == NULL)
		break;
	    free(*w.buf);
	    *w.buflen *= 2;
	    *w.buf = malloc(*w.buflen);
	    errno = old_errno;
	    if (*w.buf == NULL) {
		*w.errnop = ENOMEM;
		goto walk_nss_out;
	    }
	    goto walk_nss_morebuf;
	}
    } while (__nss_next(&nip, w.fct_name, &fct.ptr, *w.status, 0) == 0);

    if (w.buf != NULL && *w.status != NSS_STATUS_SUCCESS) {
	free(*w.buf);
	*w.buf = NULL;
    }

 walk_nss_out:
    ;
}
