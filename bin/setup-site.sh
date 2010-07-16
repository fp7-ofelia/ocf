#!/bin/bash

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

if [ -e ~/bin ] ; then
	cd $bindir
	for f in *.sh ; do
		rm ~/bin/$f
		ln -s $bindir/*.sh ~/bin
	done
	rm ~/bin/expedient-settings
	ln -s $bindir/expedient-settings ~/bin
fi

# check that DOMAIN_IP and DOMAIN_FQDN are sane:
if [ -z $DOMAIN_FQDN ] ; then
    echo "ERROR: DOMAIN_FQDN is not defined in expedient-settings!"
    exit 1
fi
if [ -z $DOMAIN_IP ] ; then
    echo "ERROR: DOMAIN_IP is not defined in expedient-settings!"
    exit 1
fi

echo Updating settings for Expedient...
# Update the settings for Expedient
sed -i "{s/^SITE_DOMAIN.*/SITE_DOMAIN = '$DOMAIN_FQDN:$CH_PORT'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^SITE_NAME.*/SITE_NAME = 'Expedient Clearinghouse at $SITE_NAME'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/<your name>/$SUPERUSER_NAME/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/<your email>/$SUPERUSER_EMAIL/}" $EXPEDIENT/src/python/$CH/deployment_settings.py

sed -i "{s/^EMAIL_USE_TLS .*/EMAIL_USE_TLS = $EMAIL_USE_TLS/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^EMAIL_HOST .*/EMAIL_HOST = '$EMAIL_HOST'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^EMAIL_HOST_USER .*/EMAIL_HOST_USER = '$EMAIL_HOST_USER'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^EMAIL_HOST_PASSWORD .*/EMAIL_HOST_PASSWORD = '$EMAIL_HOST_PASSWORD'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^EMAIL_PORT .*/EMAIL_PORT = $EMAIL_PORT/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^DEFAULT_FROM_EMAIL .*/DEFAULT_FROM_EMAIL = '$EXPEDIENT_DEFAULT_FROM_EMAIL'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/^EMAIL_SUBJECT_PREFIX .*/EMAIL_SUBJECT_PREFIX = '$EXPEDIENT_EMAIL_SUBJECT_PREFIX'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py

echo Updating settings for the Opt-in Manager...
# Update settings for the Optin manager
sed -i "{s/^SITE_DOMAIN.*/SITE_DOMAIN = '$DOMAIN_FQDN:$OM_PORT'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^SITE_NAME.*/SITE_NAME = 'Opt-In Manager at $SITE_NAME'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/<your name>/$SUPERUSER_NAME/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/<your email>/$SUPERUSER_EMAIL/}" $EXPEDIENT/src/python/$OM/deployment_settings.py

sed -i "{s/^EMAIL_USE_TLS .*/EMAIL_USE_TLS = $EMAIL_USE_TLS/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^EMAIL_HOST .*/EMAIL_HOST = '$EMAIL_HOST'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^EMAIL_HOST_USER .*/EMAIL_HOST_USER = '$EMAIL_HOST_USER'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^EMAIL_HOST_PASSWORD .*/EMAIL_HOST_PASSWORD = '$EMAIL_HOST_PASSWORD'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^EMAIL_PORT .*/EMAIL_PORT = $EMAIL_PORT/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^DEFAULT_FROM_EMAIL .*/DEFAULT_FROM_EMAIL = '$OM_DEFAULT_FROM_EMAIL'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/^EMAIL_SUBJECT_PREFIX .*/EMAIL_SUBJECT_PREFIX = '$OM_EMAIL_SUBJECT_PREFIX'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py

cd $EXPEDIENT/src/python

echo "SECRET_KEY=''" > $EXPEDIENT/src/python/$CH/secret_key.py
echo "SECRET_KEY=''" > $EXPEDIENT/src/python/$OM/secret_key.py

echo Generating secret keys...
CH_KEY=`PYTHONPATH=$PYTHONPATH python $CH/manage.py generate_secret_key`
OM_KEY=`PYTHONPATH=$PYTHONPATH python $OM/manage.py generate_secret_key`

echo Updating settings for the FlowVisor
# Setup flowvisor
cd $FLOWVISOR
make		# just to make sure it's up to date
rm -f mySSLKeyStore
# Rob, you need to set the ports here...
./scripts/config-gen-default.sh $FV_CONFIG $DOMAIN_IP $FV_ROOT_PASSWORD $FV_OF_PORT $FV_RPC_PORT

echo Setting up the databases
flush-expedient.sh
flush-om.sh

echo "SECRET_KEY = '$CH_KEY'" > $EXPEDIENT/src/python/$CH/secret_key.py
echo "SECRET_KEY = '$OM_KEY'" > $EXPEDIENT/src/python/$OM/secret_key.py

echo Updating test settings...
# fix the test_settings.py
sed -i "{s/^HOST.*/HOST = '$DOMAIN_FQDN'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^GAM_PORT.*/GAM_PORT = $GAM_PORT/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^GCH_PORT.*/GCH_PORT = $GCH_PORT/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^OM_PORT.*/OM_PORT = $OM_PORT/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^CH_PORT.*/CH_PORT = $CH_PORT/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^FV_CONFIG.*/FV_CONFIG = '$FV_CONFIG'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/host=.*,/host='$DOMAIN_IP',/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/of_port=.*,/of_port=$FV_OF_PORT,/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/xmlrpc_port=.*,/xmlrpc_port=$FV_RPC_PORT,/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^MININET_VMS.*/MININET_VMS = [('$MININET_IP', $MININET_SSH_PORT)]/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/^SHOW_PROCESSES_IN_XTERM = .*/SHOW_PROCESSES_IN_XTERM = $SHOW_PROCESSES_IN_XTERM/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/password=.*connect to the FV/password='$FV_ROOT_PASSWORD',  # The password to use to connect to the FV/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py

# webserver settings
if [ $CH_PORT != 443 ] ; then
	# hacking around apache's unwillingness to have two Listen lines on the same port
	sed -i "{s/#*Listen.*/Listen $CH_PORT/}" $EXPEDIENT/src/config/$CH/apache/vhost-clearinghouse.conf

else
	sed -i "{s/^Listen.*/#Listen $CH_PORT/}" $EXPEDIENT/src/config/$CH/apache/vhost-clearinghouse.conf
fi
sed -i "{s/Use SimpleSSLWSGIVHost .*/Use SimpleSSLWSGIVHost $CH_PORT $CH $EXPEDIENT/}" $EXPEDIENT/src/config/$CH/apache/vhost-clearinghouse.conf
sudo ln -s $EXPEDIENT/src/config/$CH/apache/vhost-clearinghouse.conf /etc/apache2/vhosts.d/

if [ $OM_PORT != 443 ] ; then
	# hacking around apache's unwillingness to have two Listen lines on the same port
	sed -i "{s/#*Listen.*/Listen $OM_PORT/}" $EXPEDIENT/src/config/$OM/apache/vhost-optinmgr.conf
else
	sed -i "{s/^Listen.*/#Listen $OM_PORT/}" $EXPEDIENT/src/config/$OM/apache/vhost-optinmgr.conf
fi
sed -i "{s/Use SimpleSSLWSGIVHost .* /Use SimpleSSLWSGIVHost $OM_PORT $OM $EXPEDIENT/}" $EXPEDIENT/src/config/$OM/apache/vhost-optinmgr.conf
sudo ln -s $EXPEDIENT/src/config/$CH/apache/vhost-optinmgr.conf /etc/apache2/vhosts.d/

sudo gensslcert -n $DOMAIN_FQDN

init-gapi-ca.sh

sudo /etc/init.d/apache2 restart

