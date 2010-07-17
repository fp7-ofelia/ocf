#!/bin/bash

echo "WARNING: This command will DELETE the expedient tree and check it back out."
echo "Make sure you have taken a snapshot you can revert to."
echo "Are you sure you want to continue? (Y/N): "; read choice

if [ X$choice != "XY" -a X$choice != "Xy" ] ; then
    exit 0
fi

# get the actual location of the setup-site script
physical=`readlink $0`
if [ $physical ]; then
	bindir=`dirname $physical`
else
	bindir=`dirname $0`
fi
settings=$bindir/expedient-settings

if [ -e `which expedient-settings` ] ; then
	source expedient-settings
elif [ -e $settings ] ; then
	source $settings
else 
	echo Could not find expedient-settings file.
	echo Please create it using expedient/bin/expedient-settings-clean as template.
fi

rm -rf $EXPEDIENT
cd ~
git clone git://openflow.org/expedient `basename $EXPEDIENT`

if [ X$1 != "X" ] ; then
	echo "Checking out $1"
	cd $EXPEDIENT
	git checkout $1
fi

cp $EXPEDIENT/bin/expedient-settings-clean $EXPEDIENT/bin/expedient-settings

cd $EXPEDIENT/src/python

cp $CH/deployment_settings_clean.py $CH/deployment_settings.py
cp $OM/deployment_settings_clean.py $OM/deployment_settings.py
cp $CH/settings_clean.py $CH/settings.py
cp $OM/settings_clean.py $OM/settings.py

rm -rf $GAPI_SSL_DIR/*

flush-om.sh
flush-expedient.sh

sudo rm -f /etc/udev/rules.d/70-persistent-net.rules

rm -f ~/.bash_history
rm -rf ~/.ssh/*
