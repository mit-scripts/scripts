/* mod_authz_afsgroup
 * version 1.1, released 2007-03-13
 * Anders Kaseorg <anders@kaseorg.com>
 *
 * This module does authorization based on AFS groups:
 *   Require afsgroup system:administrators
 *
 * It currently works by parsing the output of `pts membership
 * <group>`.
 */

#include "apr_strings.h"

#include "ap_config.h"
#include "ap_provider.h"
#include "httpd.h"
#include "http_config.h"
#include "http_core.h"
#include "http_log.h"
#include "http_protocol.h"
#include "http_request.h"

#include "mod_auth.h"

#include <unistd.h>
#include <stdio.h>

typedef struct {
    int authoritative;
} authz_afsgroup_config_rec;

static void *create_authz_afsgroup_dir_config(apr_pool_t *p, char *d)
{
    authz_afsgroup_config_rec *conf = apr_palloc(p, sizeof(*conf));

    conf->authoritative = 1;
    return conf;
}

static const command_rec authz_afsgroup_cmds[] =
{
    AP_INIT_FLAG("AuthzAFSGroupAuthoritative", ap_set_flag_slot,
                 (void *)APR_OFFSETOF(authz_afsgroup_config_rec, authoritative),
                 OR_AUTHCFG,
                 "Set to 'Off' to allow access control to be passed along to "
                 "lower modules if the 'require afsgroup' statement is not "
                 "met. (default: On)."),
    {NULL}
};

module AP_MODULE_DECLARE_DATA authz_afsgroup_module;

static authz_status is_user_in_afsgroup(request_rec *r, char* user, char* afsgroup)
{
    int pfd[2];
    pid_t cpid;
    int status;
    FILE *fp;
    char *line = NULL;
    char buf[256];
    size_t len = 0;
    ssize_t read;
    int found = 0;
    if (pipe(pfd) == -1) {
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "pipe() failed!");
	return AUTHZ_GENERAL_ERROR;
    }
    cpid = fork();
    if (cpid == -1) {
	close(pfd[0]);
	close(pfd[1]);
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "fork() failed!");
	return AUTHZ_GENERAL_ERROR;
    }
    if (cpid == 0) {
	close(pfd[0]);
	dup2(pfd[1], STDOUT_FILENO);
	execve("/usr/bin/pts",
	       (char *const[])
	       { "pts", "membership", "-nameorid", afsgroup, NULL },
	       NULL);
	_exit(1);
    }
    close(pfd[1]);
    fp = fdopen(pfd[0], "r");
    if (fp == NULL) {
	close(pfd[0]);
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "fdopen() failed!");
	return AUTHZ_GENERAL_ERROR;
    }
    if (snprintf(buf, sizeof(buf), "  %s\n", user) >= sizeof(buf)) {
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "access to %s failed, reason: username '%s' "
		      "is too long!",
		      r->uri, user);
	return AUTHZ_DENIED;
    }
    while ((read = getline(&line, &len, fp)) != -1) {
	if (strcmp(line, buf) == 0)
	    found = 1;
    }
    if (line)
	free(line);
    fclose(fp);
    if (waitpid(cpid, &status, 0) == -1) {
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "waitpid() failed!");
	return AUTHZ_GENERAL_ERROR;
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
	ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
		      "`pts membership -nameorid %s` failed!",
		      afsgroup);
	return AUTHZ_GENERAL_ERROR;
    }
    if (found)
	return AUTHZ_GRANTED;

    return AUTHZ_DENIED;
}

static authz_status check_afsgroup_access(request_rec *r,
				 const char *require_line,
				 const void *parsed_require_line)
{
    authz_afsgroup_config_rec *conf = ap_get_module_config(r->per_dir_config,
							   &authz_afsgroup_module);
    const char *t;
    char *w;
    authz_status pergroup;

    if (!r->user) {
	return AUTHZ_DENIED_NO_USER;
    }

    t = require_line;
    while ((w = ap_getword_conf(r->pool, &t)) && w[0]) {
	if ((pergroup = is_user_in_afsgroup(r, r->user, w)) != AUTHZ_DENIED) {
	    // If we got some return value other than AUTHZ_DENIED, it
	    // means we either got GRANTED, or some sort of error, and
	    // we need to bubble that up.
	    return pergroup;
	}
    }

    if (!conf->authoritative) {
        return AUTHZ_NEUTRAL;
    }

    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
                  "access to %s failed, reason: user '%s' does not meet "
                  "'require'ments for afsgroup to be allowed access",
                  r->uri, r->user);

    return AUTHZ_DENIED;
}

static const authz_provider authz_afsgroup_provider =
{
    &check_afsgroup_access,
    NULL,
};

static void register_hooks(apr_pool_t *p)
{
    ap_register_auth_provider(p, AUTHZ_PROVIDER_GROUP, "afsgroup",
                              AUTHZ_PROVIDER_VERSION,
                              &authz_afsgroup_provider, AP_AUTH_INTERNAL_PER_CONF);

}

module AP_MODULE_DECLARE_DATA authz_afsgroup_module =
{
    STANDARD20_MODULE_STUFF,
    create_authz_afsgroup_dir_config, /* dir config creater */
    NULL,                             /* dir merger --- default is to override */
    NULL,                             /* server config */
    NULL,                             /* merge server config */
    authz_afsgroup_cmds,              /* command apr_table_t */
    register_hooks                    /* register hooks */
};
