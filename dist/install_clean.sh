#!/bin/sh

source INSTALL_SETTINGS

# syncdb
echo **** Setting up the databases. Please create superuser when asked (once for
echo **** Expedient and once for the Opt-in Manager
cd $BASE/src/python $CLEARINGHOUSE/manage.py syncdb
cd $BASE/src/python $CLEARINGHOUSE/manage.py flush
cd $BASE/src/python $OPTIN_MANAGER/manage.py syncdb
cd $BASE/src/python $OPTIN_MANAGER/manage.py flush

# Set the hostname
FQDN=`hostname -f`
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = \"$FQDN\"/}" $BASE/src/python/$CLEARINGHOUSE/deployment_settings.py
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = \"$FQDN\"/}" $BASE/src/python/$OPTIN_MANAGER/deployment_settings.py

# restart apache
/etc/init.d/apache2 restart
