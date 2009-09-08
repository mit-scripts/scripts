#!/bin/sh
awk '/^18\./ && ! /^18.181/ { print $2; fflush() }' >> /var/log/httpd/statistics_log
