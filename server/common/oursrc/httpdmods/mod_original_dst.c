/* mod_original_dst
 * version 1.0, released 2011-03-25
 * Anders Kaseorg <andersk@mit.edu>
 *
 * This replaces the address of incoming connections with the original
 * destination, before any local masquerading (as given by
 * SO_ORIGINAL_DST).
 */

#include <sys/types.h>
#include <sys/socket.h>
#include <limits.h>
#include <netdb.h>
#include <linux/netfilter_ipv4.h>

#include "ap_config.h"
#include "ap_listen.h"
#include "http_config.h"
#include "http_log.h"
#include "httpd.h"
#include "mpm.h"

extern void apr_sockaddr_vars_set(apr_sockaddr_t *, int, apr_port_t);

static apr_status_t original_dst_accept_func(void **accepted, ap_listen_rec *lr, apr_pool_t *ptrans)
{
    apr_status_t status = MPM_ACCEPT_FUNC(accepted, lr, ptrans);
    if (status != APR_SUCCESS)
	return status;

    apr_socket_t *csd = *accepted;

    apr_sockaddr_t *local_addr;
    status = apr_socket_addr_get(&local_addr, APR_LOCAL, csd);
    if (status != APR_SUCCESS) {
	ap_log_perror(APLOG_MARK, APLOG_EMERG, status, ptrans,
		      "original_dst_accept_func: apr_socket_addr_get failed");
	apr_socket_close(csd);
	return APR_EGENERAL;
    }

    int sockdes;
    status = apr_os_sock_get(&sockdes, csd);
    if (status != APR_SUCCESS) {
	ap_log_perror(APLOG_MARK, APLOG_EMERG, status, ptrans,
		      "original_dst_accept_func: apr_os_sock_get failed");
	apr_socket_close(csd);
	return APR_EGENERAL;
    }

    socklen_t salen = sizeof(local_addr->sa);
    status = getsockopt(sockdes, SOL_IP, SO_ORIGINAL_DST, &local_addr->sa, &salen);
    if (status == 0) {
	local_addr->salen = salen;
	apr_sockaddr_vars_set(local_addr, local_addr->sa.sin.sin_family, htons(local_addr->sa.sin.sin_port));
	return APR_SUCCESS;
    } else if (errno == ENOENT) {
	return APR_SUCCESS;
    } else {
	ap_log_perror(APLOG_MARK, APLOG_EMERG, errno, ptrans,
		      "original_dst_accept_func: getsockopt failed");
	apr_socket_close(csd);
	return APR_EGENERAL;
    }
}

static int original_dst_post_config(apr_pool_t *pconf, apr_pool_t *plog, apr_pool_t *ptemp, server_rec *s)
{
    ap_listen_rec *lr;
    for (lr = ap_listeners; lr; lr = lr->next)
	if (lr->accept_func == MPM_ACCEPT_FUNC)
	    lr->accept_func = original_dst_accept_func;
    return OK;
}

static void original_dst_register_hooks(apr_pool_t *p)
{
    ap_hook_post_config(original_dst_post_config, NULL, NULL, APR_HOOK_MIDDLE);
}

module AP_MODULE_DECLARE_DATA original_dst_module =
{
    STANDARD20_MODULE_STUFF,
    NULL,                           /* per-directory config creator */
    NULL,                           /* dir config merger */
    NULL,                           /* server config creator */
    NULL,                           /* server config merger */
    NULL,                           /* command table */
    original_dst_register_hooks,    /* set up other request processing hooks */
};
