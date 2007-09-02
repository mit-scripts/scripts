/* mod_auth_optional
 * version 1.0, released 2007-09-01
 * Anders Kaseorg <andersk@mit.edu>
 *
 * This module can pretend that authentication succeeded even if no
 * authorization module is authoritative, instead of returning a
 * Forbidden error.
 */

#include "ap_config.h"
#include "httpd.h"
#include "http_config.h"
#include "http_request.h"

typedef struct {
    int optional;
    char *default_user;
} auth_optional_config_rec;

static void *create_auth_optional_dir_config(apr_pool_t *p, char *d)
{
    auth_optional_config_rec *conf = apr_pcalloc(p, sizeof(*conf));
    conf->optional = 0;
    conf->default_user = NULL;
    return conf;
}

static const command_rec auth_optional_cmds[] =
{
    AP_INIT_FLAG("AuthOptional", ap_set_flag_slot,
                 (void *)APR_OFFSETOF(auth_optional_config_rec, optional),
                 OR_AUTHCFG,
                 "Make authentication succeed if no authorization module is authoritative"),
    AP_INIT_TAKE1("AuthOptionalDefaultUser", ap_set_string_slot,
                   (void*)APR_OFFSETOF(auth_optional_config_rec, default_user),
                  OR_AUTHCFG,
                  "Default username to use if no authorization module is authoritative"),
    {NULL}
};

module AP_MODULE_DECLARE_DATA auth_optional_module;

static int auth_optional_check_user_id(request_rec *r)
{
    auth_optional_config_rec *conf = ap_get_module_config(r->per_dir_config,
							  &auth_optional_module);
    if (!conf->optional)
	return DECLINED;

    r->user = conf->default_user;
    return OK;
}

static int auth_optional_auth_checker(request_rec *r)
{
    auth_optional_config_rec *conf = ap_get_module_config(r->per_dir_config,
							  &auth_optional_module);
    if (!conf->optional || conf->default_user != NULL)
	return DECLINED;

    return OK;
}

static void register_hooks(apr_pool_t *p)
{
    /* Right before mod_authz_default. */
    ap_hook_check_user_id(auth_optional_check_user_id, NULL, NULL, APR_HOOK_LAST - 1);
    ap_hook_auth_checker(auth_optional_auth_checker, NULL, NULL, APR_HOOK_REALLY_FIRST);
}

module AP_MODULE_DECLARE_DATA auth_optional_module =
{
    STANDARD20_MODULE_STUFF,
    create_auth_optional_dir_config, /* dir config creater */
    NULL,                            /* dir merger --- default is to override */
    NULL,                            /* server config */
    NULL,                            /* merge server config */
    auth_optional_cmds,              /* command apr_table_t */
    register_hooks                   /* register hooks */
};
