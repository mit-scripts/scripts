#!/bin/sh
exec ansible-playbook --ask-vault-pass -i inventory.yaml playbook.yaml -u root "$@"
