/***
 * scripts.mit.edu PHP enhancement extension
 *
 * Joe Presbrey <presbrey@mit.edu>
 * 2008-06-19
 *
 ***/

#include "php.h"
#include "zend_extensions.h"

#include "php_scripts.h"

#ifndef ZEND_EXT_API
#define ZEND_EXT_API    ZEND_DLEXPORT
#endif
ZEND_EXTENSION();

ZEND_MODULE_STARTUP_D(scripts)
{
	return SUCCESS;
}

ZEND_MODULE_SHUTDOWN_D(scripts)
{
}

ZEND_MODULE_ACTIVATE_D(scripts)
{
    // replace error handler callback with our own
    old_error_cb = zend_error_cb;
    new_error_cb = scripts_error_cb;
    zend_error_cb = new_error_cb;

	return SUCCESS;
}

ZEND_MODULE_DEACTIVATE_D(scripts)
{
    // restore original error handler callback
    zend_error_cb = old_error_cb;
}

void scripts_error_cb(int type, const char *error_filename, const uint error_lineno, const char *format, va_list args)
{
    char *buffer;
    const char *user = php_get_current_user();

    // enhance the log message
    spprintf(&buffer, 0, "(%s) %s", user, format);

    // pass through to builtin error callback
    if (strncmp(format, "Module '%s' already loaded", 26)==0) {
        // demote from E_CORE_WARNING
        old_error_cb(E_NOTICE, error_filename, error_lineno, buffer, args);
    } else {
        old_error_cb(type, error_filename, error_lineno, buffer, args);
    }

    efree(buffer);
}

ZEND_DLEXPORT zend_extension zend_extension_entry = {
    PHP_SCRIPTS_EXTNAME,
    PHP_SCRIPTS_VERSION,
    PHP_SCRIPTS_AUTHOR,
    PHP_SCRIPTS_URL,
    PHP_SCRIPTS_YEAR,
    ZEND_MODULE_STARTUP_N(scripts),		/* startup_func_t */
    ZEND_MODULE_SHUTDOWN_N(scripts),	/* shutdown_func_t */
    ZEND_MODULE_ACTIVATE_N(scripts),	/* activate_func_t */
    ZEND_MODULE_DEACTIVATE_N(scripts),	/* deactivate_func_t */
    NULL,           					/* message_handler_func_t */
    NULL,           					/* op_array_handler_func_t */
    NULL,           					/* statement_handler_func_t */
    NULL,           					/* fcall_begin_handler_func_t */
    NULL,           					/* fcall_end_handler_func_t */
    NULL,           					/* op_array_ctor_func_t */
    NULL,           					/* op_array_dtor_func_t */
    STANDARD_ZEND_EXTENSION_PROPERTIES
};

#ifdef COMPILE_DL_SCRIPTS
ZEND_GET_MODULE(scripts)
#endif
