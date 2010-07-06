#!/bin/bash

echo "WARNING: This command will reset the settings and will flush the dabases."
echo "Make sure you have taken a snapshot you can revert to."
echo "Are you sure you want to continue? (Y/N): "; read choice

if [ X$choice != "XY" -a X$choice != "Xy" ] ; then
    exit 0
fi

source expedient-settings

cd $EXPEDIENT/src/python

rm -f $CH/secret_key.py*
rm -f $OM/secret_key.py*

cp $CH/deployment_settings_clean.py $CH/deployment_settings.py
cp $OM/deployment_settings_clean.py $OM/deployment_settings.py

flush-om.sh
flush-expedient.sh

sudo rm /etc/udev/rules.d/70-persistent-net.rules

rm ~/.bash_history
