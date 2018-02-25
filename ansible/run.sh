#!/bin/sh
exec ansible-playbook -i inventory.yaml playbook.yaml -u root "$@"
