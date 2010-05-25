#!/bin/sh
#
# This file installs the the Expedient Clearinghouse, plugins, and the Openflow
# Opt-In manage in an openSuSE 11.2 distro.
#
# author: Jad Naous <jnaous@stanford.edu>
#

VERSION="x.y.z"

BASE="/srv/www/expedient"
CLEARINGHOUSE="expedient/clearinghouse"
COMMON="expedient/clearinghouse"
OPTIN_MANAGER="openflow/optin_manager"

# install prereqs
zypper addrepo -f http://download.opensuse.org/repositories/devel:/languages:/python/openSUSE_11.2 python
zypper addrepo zypper addrepo -f http://download.opensuse.org/repositories/openSUSE:/11.2:/Contrib/standard/ contrib
zypper install -l python-setuptools python-django python-decorator python-django-autoslug python-m2crypto python-curl python-imaging python-django-extensions python-dateutil libxmlsec1-1 libxmlsec1-openssl1 python-paramiko python-crypto
easy_install -Z django-registration python-xmlsec1
zypper install -l -f --force-resolution libxmlsec1-openssl-devel

cp -R expedient-$VERSION $BASE

chown wwwrun:www -R $BASE
chmod g+r -R $BASE
chmod g+w -R $BASE/db

# Set the hostname
FQDN=`hostname -f`
sed -i '{s/SITE_DOMAIN.*/SITE_DOMAIN = $FQDN/}' $BASE/src/python/$CLEARINGHOUSE/settings.py
sed -i '{s/SITE_DOMAIN.*/SITE_DOMAIN = $FQDN/}' $BASE/src/python/$OPTIN_MANAGER/settings.py

# Install Apache prereqs
zypper addrepo -f http://download.opensuse.org/repositories/Apache:/Modules/openSUSE_11.2/ Apache:Modules
zypper install apache2 apache2-mod_wsgi apache2-mod_macro apache2-itk

# Add configuration
cp -s $BASE/src/config/$COMMON/apache/vhost-macros.conf /etc/apache2/conf.d/
cp -s $BASE/src/config/$CLEARINGHOUSE/apache/vhost-clearinghouse.conf /etc/apache2/vhosts.d/
cp -s $BASE/src/config/$OPTIN_MANAGER/apache/vhost-optinmgr.conf /etc/apache2/conf.d/vhosts.d/

# Create Apache log directories
mkdir -p /var/log/apache2/$CLEARINGHOUSE
mkdir -p /var/log/apache2/$OPTIN_MANAGER

# Enable various Apache flags
a2enmod wsgi
a2enmod ssl
a2enmod macro
a2enflag SSL

# Generate server certificates
/usr/bin/gensslcert

# restart apache
/etc/init.d/apache2 restart
