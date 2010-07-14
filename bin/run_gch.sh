#!/bin/bash

source expedient-settings

echo Starting the GCH in a detached screen named 'gch'...
# Run the GCH
screen -S "gch" -dm /usr/bin/python /home/expedient/expedient/src/python/gcf/gch.py -u $GAPI_SSL_DIR/experimenter.crt -r $GAPI_SSL_DIR/ca.crt -c $GAPI_SSL_DIR/ch.crt -k $GAPI_SSL_DIR/ch.key -p $GCH_PORT --debug -H 0.0.0.0 2>&1 | tee ~/gch.log
echo To access the screen, use the command: screen -rd gch
echo Output is being logged to ~/gch.log

