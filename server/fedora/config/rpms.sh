#!/bin/bash
#
# Retrieve package list from scripts.mit.edu
# Install them with yum
#
# Joe Presbrey <presbrey@mit.edu>
#
# Skip openafs (custom built), kernel (pedantic), and pubkeys.

ssh root@scripts.mit.edu rpm -qa --qf '%{name}.%{arch}\\n' | grep -v openafs | grep -v kernel | grep -v pubkey > rpms.log

yum install `cat rpms.log`
