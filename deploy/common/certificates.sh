#!/bin/bash


# XXX: Move somewhere else
source ../utils/utils.sh

accept_generate_certificates=0
if [[ ! -f /etc/apache2/ssl.crt/server.crt ]] && [[ ! -f /etc/apache2/ssl.crt/server.key ]]; then
    accept_generate_certificates="y"
fi

while [[ ! $accept_generate_certificates =~ ^[y|Y|n|N]$ ]]
    do
        echo "Do you wish to generate GID-based certificates? [y/N]"
        read accept_generate_certificates
        if [[ ! $accept_generate_certificates =~ ^[y|Y|n|N]$ ]]; then
            echo "Please accept (\"y\") or reject (\"n\") the generation"
        fi
        if [[ $accept_generate_certificates =~ ^[n|N]$ ]]; then
            echo "Certificate generation aborted by user"
            exit 1
        fi
    done

# XXX: Perform generation of GIDs

success "Certificates successfully generated"
