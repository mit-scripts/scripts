#include <krb5/localauth_plugin.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <pwd.h>

static krb5_error_code
userok_scripts(krb5_context context, krb5_localauth_moddata data,
	       krb5_const_principal aname, const char *lname) {
  // TODO: Return KRB5_PLUGIN_NO_HANDLE if some errors occur.
  krb5_error_code result = EPERM;
  char *princname = NULL;
  char pwbuf[BUFSIZ];
  struct passwd pwx, *pwd;
  int pid, status;

  /* Get the local user's homedir and uid. */
  if (getpwnam_r(luser, &pwx, pwbuf, sizeof(pwbuf), &pwd) != 0 || pwd == NULL)
    goto cleanup;

  if (krb5_unparse_name(context, principal, &princname) != 0)
    goto cleanup;

  if ((pid = fork()) == -1)
    goto cleanup;

  if (pid == 0) {
    char *args[4];
#define ADMOF_PATH "/usr/local/sbin/ssh-admof"
    args[0] = ADMOF_PATH;
    args[1] = (char *) luser;
    args[2] = princname;
    args[3] = NULL;
    execv(ADMOF_PATH, args);
    exit(1);
  }

  if (waitpid(pid, &status, 0) > 0 && WIFEXITED(status) && WEXITSTATUS(status) == 33) {
    result = 0;
  }

 cleanup:
  free(princname);
  return result;
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
