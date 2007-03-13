/* mod_authz_afsgroup
 * version 1.0, released 2006-01-04
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
#include "httpd.h"
#include "http_config.h"
#include "http_core.h"
#include "http_log.h"
#include "http_protocol.h"
#include "http_request.h"

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

static int check_afsgroup_access(request_rec *r)
{
    authz_afsgroup_config_rec *conf = ap_get_module_config(r->per_dir_config,
							   &authz_afsgroup_module);
    char *user = r->user;
    int m = r->method_number;
    int required_afsgroup = 0;
    register int x;
    const char *t;
    char *w;
    const apr_array_header_t *reqs_arr = ap_requires(r);
    require_line *reqs;

    if (!reqs_arr) {
        return DECLINED;
    }
    reqs = (require_line *)reqs_arr->elts;

    for (x = 0; x < reqs_arr->nelts; x++) {

        if (!(reqs[x].method_mask & (AP_METHOD_BIT << m))) {
            continue;
        }

        t = reqs[x].requirement;
        w = ap_getword_white(r->pool, &t);
        if (!strcasecmp(w, "afsgroup")) {
            required_afsgroup = 1;
            while (t[0]) {
		int pfd[2];
		pid_t cpid;
		int status;
		FILE *fp;
		char *line = NULL;
		char buf[256];
		size_t len = 0;
		ssize_t read;
		int found = 0;
                w = ap_getword_conf(r->pool, &t);
		if (pipe(pfd) == -1) {
		    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
				  "pipe() failed!");
		    return HTTP_INTERNAL_SERVER_ERROR;
		}
		cpid = fork();
		if (cpid == -1) {
		    close(pfd[0]);
		    close(pfd[1]);
		    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
				  "fork() failed!");
		    return HTTP_INTERNAL_SERVER_ERROR;
		}
		if (cpid == 0) {
		    close(pfd[0]);
		    dup2(pfd[1], STDOUT_FILENO);
		    execve("/usr/bin/pts",
			   (char *const[]) {
			       "pts", "membership", "-nameorid", w, NULL
			   },
			   NULL);
		    _exit(1);
		}
		close(pfd[1]);
		fp = fdopen(pfd[0], "r");
		if (fp == NULL) {
		    close(pfd[0]);
		    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
				  "fdopen() failed!");
		    return HTTP_INTERNAL_SERVER_ERROR;
		}
		if (snprintf(buf, sizeof(buf), "  %s\n", user) >= sizeof(buf)) {
		    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
				  "access to %s failed, reason: username '%s' "
				  "is too long!",
				  r->uri, user);
		    continue;
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
		    return HTTP_INTERNAL_SERVER_ERROR;
		}
		if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
		    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
				  "`pts membership -nameorid %s` failed!",
				  w);
		    return HTTP_INTERNAL_SERVER_ERROR;
		}
		if (found)
		    return OK;
            }
        }
    }

    if (!required_afsgroup) {
        return DECLINED;
    }

    if (!conf->authoritative) {
        return DECLINED;
    }

    ap_log_rerror(APLOG_MARK, APLOG_ERR, 0, r,
                  "access to %s failed, reason: user '%s' does not meet "
                  "'require'ments for afsgroup to be allowed access",
                  r->uri, user);

    ap_note_auth_failure(r);
    return HTTP_FORBIDDEN;
}

static void register_hooks(apr_pool_t *p)
{
    ap_hook_auth_checker(check_afsgroup_access, NULL, NULL, APR_HOOK_MIDDLE);
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
