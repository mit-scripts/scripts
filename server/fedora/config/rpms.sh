#!/bin/bash

# Retrieve package list from scripts.mit.edu

ssh root@scripts.mit.edu rpm -qa --qf '%{name}.%{arch}\\n' | grep -v openafs | grep -v kernel | grep -v pubkey > rpms.log

yum install `cat rpms.log`
