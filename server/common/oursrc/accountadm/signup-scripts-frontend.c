/*
 * signup-scripts-frontend
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

extern char **environ;

int main(int argc, char **argv) {
	environ=NULL;
	if(argc != 2) {
		exit(1);
	}

	char uid[21]; // 64-bit uid requires 21
	int retval = snprintf(uid, 21, "%d", getuid());
	if(retval < 0 || retval >= 21) {
		exit(1);
	}
	if(setreuid(geteuid(), -1) != 0) {
		exit(1);
	}
	char *v[3];
#define BACKEND_PATH "/usr/local/sbin/signup-scripts-backend"
	v[0] = BACKEND_PATH;
	v[1] = argv[1];
	v[2] = NULL;
	execv(BACKEND_PATH, v);
	return 1;
}
