#!/bin/bash

set -e
set -x

cd /srv/repository/ansible
ansible-playbook playbook.yml -c local -l "localhost,$(hostname -f),$(hostname -s),127.0.0.1" --diff -v

systemctl disable ansible-config-me.service
