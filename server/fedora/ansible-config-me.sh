#!/bin/bash

set -e
set -x

cd /srv/repository/ansible
ansible-playbook playbook.yml

systemctl disable ansible-config-me.service
