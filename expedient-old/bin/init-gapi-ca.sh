#!/bin/bash

source expedient-settings

# initialize the CA used for the GENI API
mkdir -p $GAPI_SSL_DIR/certs
python $EXPEDIENT/src/python/gcf/init-ca.py -d $GAPI_SSL_DIR --am --ch --ca --exp
rm -f $GAPI_SSL_DIR/certs/ca.crt
ln -s $GAPI_SSL_DIR/ca.crt /$GAPI_SSL_DIR/certs/
rm -f $GAPI_SSL_DIR/certs/ch.crt
ln -s $GAPI_SSL_DIR/ch.crt /$GAPI_SSL_DIR/certs/

