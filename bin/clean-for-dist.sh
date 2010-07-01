#!/bin/bash

source expedient-settings

cd $EXPEDIENT/src/python

cp $CH/deployment_settings_clean.py $CH/deployment_settings.py
cp $OM/deployment_settings_clean.py $OM/deployment_settings.py

flush-om.sh
flush-expedient.sh

sudo rm /etc/udev/rules.d/70-persistent-net.rules
