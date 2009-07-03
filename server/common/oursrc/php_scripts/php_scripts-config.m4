PHP_ARG_ENABLE(scripts, whether to enable scripts.mit.edu support,
[ --enable-scripts   Enable scripts.mit.edu support])

if test "$PHP_SCRIPTS" != "no"; then
  AC_DEFINE(HAVE_SCRIPTS, 1, [Whether you have scripts.mit.edu support])
  PHP_NEW_EXTENSION(scripts, php_scripts.c, $ext_shared)
fi
