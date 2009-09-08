#!/bin/sh
perl -ne 'BEGIN { $| = 1 }
next unless /^18\./;
next if /^18\.181\./;
chomp; split;
if ($_[1] eq "scripts.mit.edu" && $_[2] =~ m|/(~[^/]+)/|) {
print "$1\n";
} else {
print "$_[1]\n";
}' >> /var/log/httpd/statistics_log
#awk '/^18\./ && ! /^18.181/ { print $2; fflush() }' >> /var/log/httpd/statistics_log
