#!/bin/bash

source expedient-settings

echo Starting the GCH in a detached screen named 'gch'...
# Run the GCH
screen -S "gch" -dm /usr/bin/python /home/expedient/expedient/src/python/gcf/gch.py -r $GAPI_SSL_DIR/ca.crt -c $GAPI_SSL_DIR/ch.crt -k $GAPI_SSL_DIR/ch.key -p $GCH_PORT --debug -H 0.0.0.0
echo To access the screen, use the command: screen -rd gch

