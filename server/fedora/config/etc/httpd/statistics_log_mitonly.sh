#!/bin/sh
awk '/^18\./ && ! /^18.181/ { print $2 }' >> /var/log/httpd/statistics_log
