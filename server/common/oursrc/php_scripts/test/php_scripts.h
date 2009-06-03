/***
 * scripts.mit.edu PHP extension
 *
 * Joe Presbrey <presbrey@mit.edu>
 * 2008-06-19
 *
 ***/

#ifndef PHP_SCRIPTS_H
#define PHP_SCRIPTS_H 1

#define PHP_SCRIPTS_VERSION "1.0"
#define PHP_SCRIPTS_EXTNAME "scripts"
#define PHP_SCRIPTS_AUTHOR "presbrey@mit.edu"
#define PHP_SCRIPTS_URL "http://scripts.mit.edu/"
#define PHP_SCRIPTS_YEAR "2008"

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

extern zend_module_entry scripts_module_entry;
#define phpext_scripts_ptr &scripts_module_entry

/* error callback repalcement functions */
void (*old_error_cb)(int type, const char *error_filename, const uint error_lineno, const char *format, va_list args);
void (*new_error_cb)(int type, const char *error_filename, const uint error_lineno, const char *format, va_list args);
void scripts_error_cb(int type, const char *error_filename, const uint error_lineno, const char *format, va_list args);

static function_entry scripts_functions[] = {
    {NULL, NULL, NULL}
};

zend_module_entry scripts_module_entry = {
#if ZEND_MODULE_API_NO >= 20010901
    STANDARD_MODULE_HEADER,
#endif
    PHP_SCRIPTS_EXTNAME,
    scripts_functions,
    NULL, //PHP_MINIT(scripts),
    NULL, //PHP_MSHUTDOWN(scripts),
    NULL,
    NULL,
    NULL,
#if ZEND_MODULE_API_NO >= 20010901
    PHP_SCRIPTS_VERSION,
#endif
    STANDARD_MODULE_PROPERTIES
};

#endif
