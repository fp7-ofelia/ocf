#!/bin/bash

source expedient-settings

# initialize the CA used for the GENI API
mkdir -p $GAPI_SSL_DIR/certs
python /home/expedient/expedient/src/python/gcf/init-ca.py -d $GAPI_SSL_DIR --am --ch --ca --exp
ln -s $GAPI_SSL_DIR/*.crt /$GAPI_SSL_DIR/certs/

