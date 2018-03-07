#!/bin/sh
export ANSIBLE_PIPELINING=True
exec ansible-playbook -i inventory.yaml playbook.yaml -u root "$@"
