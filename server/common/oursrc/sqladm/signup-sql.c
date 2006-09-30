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
#define BUFLEN 128
	char buf[NUMBUF][BUFLEN];
	char *env[NUMBUF+1];
	int i = 0;
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "HOME", "/home/sql");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "TERM", "xterm");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "USER", "sql");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "SHELL", "/usr/local/bin/bash");
	snprintf(buf[i++], BUFLEN-1, "%s=%s", "PATH", "/usr/kerberos/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin");
	for(i = 0; i < NUMBUF; i++) {
		env[i] = buf[i];
	}
	env[i] = NULL;

	char uid[21]; // 64-bit uid requires 21
	char gid[21]; // 64-bit gid requires 21
	int retval = snprintf(uid, 21, "%d", getuid());
	if(retval < 0 || retval >= 21) {
                exit(1);
        }
	retval = snprintf(gid, 21, "%d", getgid());
	if(retval < 0 || retval >= 21) {
		exit(1);
	}

        char *v[5];
#define SIGNUP_PATH "/afs/athena.mit.edu/contrib/sql/web_scripts/main/batch/signup.php"
        v[0] = SIGNUP_PATH;
	v[1] = getpwuid(getuid())->pw_name;
	v[2] = uid;
	v[3] = gid;
        v[4] = NULL;

	if(setregid(SQL_GID, SQL_GID) != 0) {
		exit(1);
	}
	if(setreuid(SQL_UID, SQL_UID) != 0) {
		exit(1);
	}

        execle(SIGNUP_PATH, v, env);
	return 1;
}
