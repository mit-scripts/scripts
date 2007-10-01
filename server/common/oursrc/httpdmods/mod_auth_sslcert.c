/* mod_auth_sslcert
 * version 1.1.1, released 2007-10-01
 * Anders Kaseorg <andersk@mit.edu>
 *
 * This module does authentication based on SSL client certificates:
 *   AuthType SSLCert
 *   AuthSSLCertVar SSL_CLIENT_S_DN_Email
 *   AuthSSLCertStripSuffix "@MIT.EDU"
 */

#include "apr_strings.h"
#define APR_WANT_STRFUNC        /* for strcasecmp */
#include "apr_want.h"

#include "ap_config.h"
#include "httpd.h"
#include "http_config.h"
#include "http_core.h"
#include "http_log.h"
#include "http_request.h"

#include "mod_auth.h"
#include "mod_ssl.h"

static APR_OPTIONAL_FN_TYPE(ssl_var_lookup) *ssl_var_lookup;

typedef struct {
    int authoritative;
    char *var;
    char *strip_suffix;
    int strip_suffix_required;
} auth_sslcert_config_rec;

static void *create_auth_sslcert_dir_config(apr_pool_t *p, char *dirspec)
{
    auth_sslcert_config_rec *conf = apr_pcalloc(p, sizeof(*conf));

    conf->authoritative = -1;
    conf->var = NULL;
    conf->strip_suffix = NULL;
    conf->strip_suffix_required = -1;

    return conf;
}

static void *merge_auth_sslcert_dir_config(apr_pool_t *p, void *parent_conf, void *newloc_conf)
{
    auth_sslcert_config_rec *pconf = parent_conf, *nconf = newloc_conf,
	*conf = apr_pcalloc(p, sizeof(*conf));

    conf->authoritative = (nconf->authoritative != -1) ?
	nconf->authoritative : pconf->authoritative;
    conf->var = (nconf->var != NULL) ?
	nconf->var : pconf->var;
    conf->strip_suffix = (nconf->var != NULL || nconf->strip_suffix != NULL) ?
	nconf->strip_suffix : pconf->strip_suffix;
    conf->strip_suffix_required = (nconf->var != NULL || nconf->strip_suffix_required != -1) ?
	nconf->authoritative : pconf->authoritative;

    return conf;
}

static const command_rec auth_sslcert_cmds[] =
{
    AP_INIT_FLAG("AuthSSLCertAuthoritative", ap_set_flag_slot,
                 (void *)APR_OFFSETOF(auth_sslcert_config_rec, authoritative),
                 OR_AUTHCFG,
                 "Set to 'Off' to allow access control to be passed along to "
                 "lower modules if the UserID is not known to this module"),
    AP_INIT_TAKE1("AuthSSLCertVar", ap_set_string_slot,
		  (void*)APR_OFFSETOF(auth_sslcert_config_rec, var),
		  OR_AUTHCFG,
		  "SSL variable to use as the username"),
    AP_INIT_TAKE1("AuthSSLCertStripSuffix", ap_set_string_slot,
		  (void*)APR_OFFSETOF(auth_sslcert_config_rec, strip_suffix),
		  OR_AUTHCFG,
		  "An optional suffix to strip from the username"),
    AP_INIT_FLAG("AuthSSLCertStripSuffixRequired", ap_set_flag_slot,
		 (void *)APR_OFFSETOF(auth_sslcert_config_rec, strip_suffix_required),
		 OR_AUTHCFG,
		 "Set to 'Off' to allow certs that don't end with a recognized "
		 "suffix to still authenticate"),
    {NULL}
};

module AP_MODULE_DECLARE_DATA auth_sslcert_module;

static int authenticate_sslcert_user(request_rec *r)
{
    auth_sslcert_config_rec *conf = ap_get_module_config(r->per_dir_config,
							 &auth_sslcert_module);
    const char *current_auth;

    /* Are we configured to be SSLCert auth? */
    current_auth = ap_auth_type(r);
    if (!current_auth || strcasecmp(current_auth, "SSLCert") != 0) {
        return DECLINED;
    }

    r->ap_auth_type = "SSLCert";

    if (strcasecmp((char *)ssl_var_lookup(r->pool, r->server, r->connection, r,
					  "SSL_CLIENT_VERIFY"),
		   "SUCCESS") == 0) {
	if (conf->var == NULL) {
	    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
			  "AuthSSLCertVar is not set: \"%s\"", r->uri);
	    return HTTP_INTERNAL_SERVER_ERROR;
	}
	char *user = (char *)ssl_var_lookup(r->pool, r->server, r->connection, r,
					    conf->var);
	if (user != NULL && user[0] != '\0') {
	    if (conf->strip_suffix != NULL) {
		int i = strlen(user) - strlen(conf->strip_suffix);
		if (i >= 0 && strcasecmp(user + i, conf->strip_suffix) == 0) {
		    r->user = apr_pstrmemdup(r->pool, user, i);
		    return OK;
		} else if (!conf->strip_suffix_required) {
		    r->user = user;
		    return OK;
		} else {
		    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
				  "SSL username for \"%s\" has wrong suffix: \"%s\"",
				  r->uri, user);
		}
	    } else {
		r->user = user;
		return OK;
	    }
	} else {
	    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
			  "no SSL username for \"%s\"", r->uri);
	}
    } else if (conf->authoritative) {
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "SSL client not verified for \"%s\"", r->uri);
    }

    /* If we're not authoritative, then any error is ignored. */
    if (!conf->authoritative) {
	return DECLINED;
    }

    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		  "SSLCert authentication failure for \"%s\"",
		  r->uri);
    return HTTP_UNAUTHORIZED;
}

static void import_ssl_var_lookup()
{
    ssl_var_lookup = APR_RETRIEVE_OPTIONAL_FN(ssl_var_lookup);
}

static void register_hooks(apr_pool_t *p)
{
    ap_hook_check_user_id(authenticate_sslcert_user, NULL, NULL, APR_HOOK_MIDDLE);
    ap_hook_optional_fn_retrieve(import_ssl_var_lookup, NULL, NULL, APR_HOOK_MIDDLE);
}

module AP_MODULE_DECLARE_DATA auth_sslcert_module =
{
    STANDARD20_MODULE_STUFF,
    create_auth_sslcert_dir_config,  /* dir config creater */
    merge_auth_sslcert_dir_config,   /* dir merger */
    NULL,                            /* server config */
    NULL,                            /* merge server config */
    auth_sslcert_cmds,               /* command apr_table_t */
    register_hooks                   /* register hooks */
};
