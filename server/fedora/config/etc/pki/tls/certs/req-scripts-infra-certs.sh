#!/bin/bash

set -euf
set -x

while read HOST FILE; do
    yes "" | openssl req -key /etc/pki/tls/private/scripts-2048.key -new -sha256 -reqexts SAN -config <(cat /etc/pki/tls/openssl.cnf <(printf "[req_distinguished_name]\ncommonName_default=$HOST\n[SAN]\nsubjectAltName=DNS:$HOST\n")) -out $FILE.csr
done <<EOF
scripts.mit.edu          scripts
scripts-cert.mit.edu     scripts-cert
*.scripts.mit.edu        star.scripts
EOF
