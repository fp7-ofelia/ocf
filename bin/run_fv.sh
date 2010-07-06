#!/bin/bash

source expedient-settings

echo Starting the Flowvisor in a detached screen named 'flowvisor'...
# Run the Flowvisor
cd ~/flowvisor
screen -S "flowvisor" -dm ./scripts/flowvisor.sh ./$FV_CONFIG 2>&1 | tee ~/flowvisor.log
echo To access the screen, use the command: screen -rd flowvisor
echo Output is being logged to ~/flowvisor.log
