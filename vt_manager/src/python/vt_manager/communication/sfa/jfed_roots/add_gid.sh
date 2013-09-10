#!/bin/bash

FILE=$1
# checking file exist or not
if [ ! -f $FILE ]; then
    echo "$FILE : does not exists";
    exit 1
elif [ ! -r $FILE ]; then
    echo "$FILE: can not read";
    exit 2
fi

if [ "${FILE##*.}" = "gid" ]; then
    HASH=$(openssl x509 -noout -hash -in $FILE)
    cd /etc/apache2/ssl.crt/ca_clients/
    ln -s /opt/ofelia/optin_manager/src/python/openflow/optin_manager/sfa/jfed_roots/$FILE $HASH.0
else
    echo "File extension must be .gid";
fi

