#!/bin/bash

source expedient-settings

echo Starting the GAM in a detached screen named gam...
# Run the GAM
screen -S "gam" -dm /usr/bin/python /home/expedient/expedient/src/python/gcf/gam.py -u https://localhost:443/openflow/gapi/ -u $GAPI_SSL_DIR/experimenter.crt -r $GAPI_SSL_DIR -c $GAPI_SSL_DIR/server.crt -k $GAPI_SSL_DIR/server.key -p $GAM_PORT --debug -H 0.0.0.0 2>&1 | tee ~/gam.log
echo To access the screen, use the command: screen -rd gam
echo Output is being logged to ~/gam.log
