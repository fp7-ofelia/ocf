#!/bin/bash

echo "WARNING: This command will DELETE the expedient tree and check it back out."
echo "Make sure you have taken a snapshot you can revert to."
echo "Are you sure you want to continue? (Y/N): "; read choice

if [ X$choice != "XY" -a X$choice != "Xy" ] ; then
    exit 0
fi

if [ -e $EXPEDIENT/bin/expedient-settings ] ; then
	source $EXPEDIENT/bin/expedient-settings
else
	source $EXPEDIENT/bin/expedient-settings-clean
fi

rm -rf $EXPEDIENT
git clone git://openflow.org/expedient $EXPEDIENT

if [ X$1 != "X" ] ; then
	echo "Checking out $1"
	cd $EXPEDIENT
	git checkout $1
fi

cp $EXPEDIENT/bin/expedient-settings-clean $EXPEDIENT/bin/expedient-settings

cd $EXPEDIENT/src/python

cp $CH/deployment_settings_clean.py $CH/deployment_settings.py
cp $OM/deployment_settings_clean.py $OM/deployment_settings.py

rm -rf $GAPI_SSL_DIR/*

flush-om.sh
flush-expedient.sh

sudo rm -f /etc/udev/rules.d/70-persistent-net.rules

rm -f ~/.bash_history
rm -rf ~/.ssh/*
