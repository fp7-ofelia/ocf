#!/bin/bash

# Argument: GID file under "trusted_roots" folders
FILE=$(basename $1)

# Ensure GID file exists
current_dir=$PWD
cd trusted_roots
if [ ! -f $FILE ]; then
    echo "$FILE : does not exists";
    exit 1
elif [ ! -r $FILE ]; then
    echo "$FILE: can not read";
    exit 2
fi

if [ "${FILE##*.}" = "gid" ]; then
    HASH=$(openssl x509 -noout -hash -in $FILE)
    ca_clients_folder="/etc/apache2/ssl.crt/ca_clients/"
    #ln -s /opt/ofelia/optin_manager/src/python/openflow/optin_manager/sfa/jfed_roots/$FILE $HASH.0
    # Symbolink link from Apache's CA client folder to Opt-in manager's SFA trusted roots folder
    ln -s $PWD/$FILE $ca_clients_folder/$HASH.0
else
    echo "File extension must be .gid";
fi

cd $current_dir

