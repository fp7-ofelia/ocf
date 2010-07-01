#!/bin/bash

source expedient-settings

echo Updating settings for Expedient...
# Update the settings for Expedient
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = '$DOMAIN_FQDN:$CH_PORT'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/SITE_NAME.*/SITE_NAME = 'Expedient Clearinghouse at $SITE_NAME'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/<your name>/$SUPERUSER_NAME/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/<your email>/$SUPERUSER_EMAIL/}" $EXPEDIENT/src/python/$CH/deployment_settings.py

sed -i "{s/EMAIL_USE_TLS .*/EMAIL_USE_TLS = $EMAIL_USE_TLS/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/EMAIL_HOST .*/EMAIL_HOST = '$EMAIL_HOST'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/EMAIL_HOST_USER .*/EMAIL_HOST_USER = '$EMAIL_HOST_USER'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/EMAIL_HOST_PASSWORD .*/EMAIL_HOST_PASSWORD = '$EMAIL_HOST_PASSWORD'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/EMAIL_PORT .*/EMAIL_PORT = '$EMAIL_PORT'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/DEFAULT_FROM_EMAIL .*/DEFAULT_FROM_EMAIL = '$EXPEDIENT_DEFAULT_FROM_EMAIL'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py
sed -i "{s/EMAIL_SUBJECT_PREFIX .*/EMAIL_SUBJECT_PREFIX = '$EXPEDIENT_EMAIL_SUBJECT_PREFIX'/}" $EXPEDIENT/src/python/$CH/deployment_settings.py

echo Updating settings for the Opt-in Manager...
# Update settings for the Optin manager
sed -i "{s/SITE_DOMAIN.*/SITE_DOMAIN = '$DOMAIN_FQDN:$OM_PORT'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/SITE_NAME.*/SITE_NAME = 'Opt-In Manager at $SITE_NAME'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/<your name>/$SUPERUSER_NAME/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/<your email>/$SUPERUSER_EMAIL/}" $EXPEDIENT/src/python/$OM/deployment_settings.py

sed -i "{s/EMAIL_USE_TLS .*/EMAIL_USE_TLS = $EMAIL_USE_TLS/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/EMAIL_HOST .*/EMAIL_HOST = '$EMAIL_HOST'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/EMAIL_HOST_USER .*/EMAIL_HOST_USER = '$EMAIL_HOST_USER'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/EMAIL_HOST_PASSWORD .*/EMAIL_HOST_PASSWORD = '$EMAIL_HOST_PASSWORD'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/EMAIL_PORT .*/EMAIL_PORT = '$EMAIL_PORT'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/DEFAULT_FROM_EMAIL .*/DEFAULT_FROM_EMAIL = '$OM_DEFAULT_FROM_EMAIL'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py
sed -i "{s/EMAIL_SUBJECT_PREFIX .*/EMAIL_SUBJECT_PREFIX = '$OM_EMAIL_SUBJECT_PREFIX'/}" $EXPEDIENT/src/python/$OM/deployment_settings.py

cd $EXPEDIENT/src/python

echo "SECRET_KEY=''" > $EXPEDIENT/src/python/$CH/secret_key.py
echo "SECRET_KEY=''" > $EXPEDIENT/src/python/$OM/secret_key.py

echo Generating secret keys...
CH_KEY=`PYTHONPATH=$PYTHONPATH python $CH/manage.py generate_secret_key`
OM_KEY=`PYTHONPATH=$PYTHONPATH python $OM/manage.py generate_secret_key`

echo Setting up the databases
flush-expedient.sh
flush-om.sh

python $CH/manage.py runscript create-superuser
python $OM/manage.py runscript create-superuser

echo "SECRET_KEY = '$CH_KEY'" > $EXPEDIENT/src/python/$CH/secret_key.py
echo "SECRET_KEY = '$OM_KEY'" > $EXPEDIENT/src/python/$OM/secret_key.py

echo Updating test settings...
# fix the test_settings.py
sed -i "{s/HOST.*/HOST = '$DOMAIN_FQDN'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/OM_PORT.*/OM_PORT = '$OM_PORT'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/CH_PORT.*/CH_PORT = '$CH_PORT'/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/host=.*/host='$DOMAIN_IP',/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py
sed -i "{s/MININET_VMS.*/MININET_VMS = [('$MININET_IP', $MININET_SSH_PORT)]/}" $EXPEDIENT/src/python/openflow/tests/test_settings.py

sudo gensslcert -n $DOMAIN_FQDN

sudo /etc/init.d/apache2 restart
