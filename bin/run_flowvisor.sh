#!/bin/bash

source expedient-settings

echo Starting the FlowVisor in a detached screen named flowvisor...
# Run the FV
screen -S "flowvisor" -L -dm $FLOWVISOR/scripts/flowvisor.sh $FLOWVISOR/default-config.xml
echo To access the screen, use the command: screen -rd flowvisor
