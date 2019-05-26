#include <krb5/localauth_plugin.h>

static krb5_error_code
userok_scripts(krb5_context context, krb5_localauth_moddata data,
	       krb5_const_principal aname, const char *lname) {
  return KRB5_PLUGIN_NO_HANDLE;
}

krb5_error_code
localauth_scripts_initvt(krb5_context context, int maj_ver, int min_ver,
			 krb5_plugin_vtable vtable)
{
  if (maj_ver == 1) {
    krb5_localauth_vtable vt = (krb5_localauth_vtable)vtable;

    vt->name = "scripts";
    vt->userok = userok_test;
    return 0;
  }
  return KRB5_PLUGIN_VER_NOTSUPP;
}
