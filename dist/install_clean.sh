#!/bin/sh

source ./install_settings

# syncdb
python $BASE/src/python/$OPTIN_MANAGER/manage.py syncdb
python $BASE/src/python/$OPTIN_MANAGER/manage.py flush
python $BASE/src/python/$CLEARINGHOUSE/manage.py syncdb
python $BASE/src/python/$CLEARINGHOUSE/manage.py flush


# Set the hostname
FQDN=`hostname -f`
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = \"$FQDN\"/}" $BASE/src/python/$CLEARINGHOUSE/deployment_settings.py
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = \"$FQDN\"/}" $BASE/src/python/$OPTIN_MANAGER/deployment_settings.py

# restart apache
/etc/init.d/apache2 restart
