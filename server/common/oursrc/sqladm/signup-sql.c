/*
 * signup-sql
 * Copyright (C) 2006  Jeff Arnold <jbarnold@mit.edu>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 *
 * See /COPYRIGHT in this repository for more information.
 */

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h> // for getpwnam
#include <pwd.h> // for getpwnam

int main(int argc, char **argv) {
        if(argc != 1) {
		exit(1);
	}

#define NUMBUF 5
#define BUFLEN 256
	char buf[NUMBUF][BUFLEN];
	char *env[NUMBUF+1];
	int i = 0;
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "HOME", "/afs/athena.mit.edu/contrib/sql");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "TERM", "xterm");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "USER", "sql");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "SHELL", "/usr/local/bin/bash");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "PATH", "/usr/kerberos/sbin:/usr/kerberos/bin:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin");
	for(i = 0; i < NUMBUF; i++) {
		env[i] = buf[i];
	}
	env[i] = NULL;

	char uid_str[21]; // 64-bit uid requires 21
	char gid_str[21]; // 64-bit gid requires 21
	int uid_num = getuid();
	int retval = snprintf(uid_str, 21, "%d", uid_num);
	if(retval < 0 || retval >= 21) {
                exit(1);
        }
	retval = snprintf(gid_str, 21, "%d", getgid());
	if(retval < 0 || retval >= 21) {
		exit(1);
	}

	if(setregid(SQL_GID, SQL_GID) != 0) {
		exit(1);
	}
	if(setreuid(SQL_UID, SQL_UID) != 0) {
		exit(1);
	}

#define SIGNUP_PATH "/afs/athena.mit.edu/contrib/sql/web_scripts/main/batch/signup.php"
        execle(SIGNUP_PATH, SIGNUP_PATH, getpwuid(uid_num)->pw_name, uid_str, gid_str, NULL, env);
	return 1;
}
