#!/bin/bash

source expedient-settings

# Update the settings for Expedient
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = '$DOMAIN_FQDN'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/SITE_NAME.*/SITE_NAME = 'Expedient Clearinghouse at $SITE_NAME'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/<your name>/$SUPERUSER_NAME/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/<your email>/$SUPERUSER_EMAIL/}" $EXPEDIENT/src/python/$CH/deployment_settings.py

# Update settings for the Optin manager
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = '$DOMAIN_FQDN'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/SITE_NAME.*/SITE_NAME = 'Opt-In Manager at $SITE_NAME'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/<your name>/$SUPERUSER_NAME/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/<your email>/$SUPERUSER_EMAIL/}" $EXPEDIENT/src/python/$OM/deployment_settings.py

cd $EXPEDIENT/src/python

flush-expedient.sh
flush-om.sh

python $CH/manage.py runscript create_superuser
python $OM/manage.py runscript create_superuser

echo > $EXPEDIENT/src/python/$CH/secret_key.py
echo > $EXPEDIENT/src/python/$OM/secret_key.py

CH_KEY=`python $CH/manage.py generate_secret_key`
OM_KEY=`python $OM/manage.py generate_secret_key`

echo "SECRET_KEY = '$CH_KEY'" > $EXPEDIENT/src/python/$CH/secret_key.py
echo "SECRET_KEY = '$OM_KEY'" > $EXPEDIENT/src/python/$OM/secret_key.py

# fix the test_settings.py
sed -i "{s/HOST.*/HOST = '$DOMAIN_FQDN'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/OM_PORT.*/OM_PORT = '$OM_PORT'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/CH_PORT.*/CH_PORT = '$CH_PORT'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/host=.*/host='$DOMAIN_IP'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/MININET_VMS.*/MININET_VMS = [('$MININET_IP', MININET_SSH_PORT)]/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py

sudo gensslcert -n $DOMAIN_FQDN

sudo /etc/init.d/apache2 restart
