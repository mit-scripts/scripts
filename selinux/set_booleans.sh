#!/bin/bash

setsebool -P \
	allow_gssd_read_tmp=1 \
	allow_httpd_anon_write=1 \
	allow_httpd_staff_script_anon_write=1 \
	allow_httpd_sys_script_anon_write=1 \
	allow_httpd_sysadm_script_anon_write=1 \
	allow_httpd_user_script_anon_write=1 \
	allow_java_execstack=1 \
	allow_kerberos=1 \
	allow_mounton_anydir=1 \
	allow_nfsd_anon_write=1 \
	allow_ssh_keysign=1 \
	allow_user_mysql_connect=1 \
	cron_can_relabel=1 \
	httpd_builtin_scripting=1 \
	httpd_can_network_connect=1 \
	httpd_can_network_connect_db=1 \
	httpd_can_network_relay=1 \
	httpd_enable_cgi=1 \
	httpd_enable_homedirs=1 \
	httpd_ssi_exec=1 \
	httpd_tty_comm=1 \
	nfs_export_all_ro=1 \
	nfs_export_all_rw=1 \
	ssh_sysadm_login=1 \
	use_nfs_home_dirs=1 \
	use_samba_home_dirs=1 \
	user_ping=1 \
	user_rw_noexattrfile=1 \
	user_tcp_server=1
#	allow_daemons_use_tty=1 \
#	allow_mount_anyfile=1 \
#	staff_read_sysadm_file=1 \
