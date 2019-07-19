#!/bin/bash

set -e
set -x

cd /srv/repository/ansible
ansible-playbook playbook.yml -c local -l "localhost,$(hostname -f | tr '[:upper:]' '[:lower:]'),$(hostname -s | tr '[:upper:]' '[:lower:]'),127.0.0.1" --diff -v

touch /etc/ansible-config-done
