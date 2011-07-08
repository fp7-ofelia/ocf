#!/bin/sh

source ./install_settings

sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = \"$CH_FQDN\"/}" $BASE/src/python/$CLEARINGHOUSE/deployment_settings.py
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = \"$OM_FQDN\"/}" $BASE/src/python/$OPTIN_MANAGER/deployment_settings.py

# syncdb
python $BASE/src/python/$OPTIN_MANAGER/manage.py syncdb
python $BASE/src/python/$CLEARINGHOUSE/manage.py syncdb

# restart apache
/etc/init.d/apache2 restart

