#!/bin/sh
#
# This file installs the the Expedient Clearinghouse, plugins, and the Openflow
# Opt-In manage in an openSuSE 11.2 distro.
#
# author: Jad Naous <jnaous@stanford.edu>
#

source ./install_settings

# Configs to do:
# Edit Django Settings:
# ---------------------
# edit the <egeni_root>/src/python/expedient/clearinghouse/settings.py and:
# 1. Set the database parameters (see the Django documentation).
# 2. Set the SITE_DOMAIN to your host's address
# 3. Set the SITE_NAME to what you would like to call your site
# 4. Go through other settings to make sure they're all applicable.

# Also edit src/python/openflow/optin_manger/settings.py
# ADMINS
# DB Engine if not sqlite3
# TIME_ZONE
# EMAIL_*
# SITE_DOMAIN
# MY_CA

# Edit the <egeni_root>/src/config/expedient/clearinghouse/apache/vhost-clearinghouse.conf and point
# it to the correct <egeni_root> and set the correct port to listen to if different from default
# Ditto src/config/openflow/optin_manager/apache/vhost-optinmgr.conf - but shouldnt need to change it

# install prereqs
zypper -n addrepo -f http://download.opensuse.org/repositories/devel:/languages:/python/openSUSE_11.2 python
zypper -n addrepo -f http://download.opensuse.org/repositories/openSUSE:/11.2:/Contrib/standard/ contrib
zypper -n install -l python-setuptools python-django python-decorator python-django-autoslug python-m2crypto python-curl python-imaging python-django-extensions python-dateutil libxml libxml2 gcc libxmlsec1-1 libxmlsec1-openssl1 python-paramiko python-crypto python-django-renderform python-webob sqlite3 python-openssl gcc

easy_install -Z django-registration pyquery

echo **** Ignore errors next and force the install option 2:
zypper install -l -f --force-resolution libxmlsec1-openssl-devel

cp -R ../expedient-$VERSION $BASE

chown -R wwwrun:www $BASE
chmod -R g+r $BASE
chmod -R g+w $BASE/db
chgrp www /etc/apache2/ssl.crt
chmod g+rw /etc/apache2/ssl.crt

# Install Apache prereqs
zypper -n addrepo -f http://download.opensuse.org/repositories/Apache:/Modules/openSUSE_11.2/ Apache:Modules
zypper -n install apache2 apache2-mod_wsgi apache2-mod_macro apache2-itk

# Add configuration
cp -s $BASE/src/config/$COMMON/apache/vhost-macros.conf /etc/apache2/conf.d/
cp -s $BASE/src/config/$CLEARINGHOUSE/apache/vhost-clearinghouse.conf /etc/apache2/vhosts.d/
cp -s $BASE/src/config/$OPTIN_MANAGER/apache/vhost-optinmgr.conf /etc/apache2/vhosts.d/

# Create Apache log directories
mkdir -p /var/log/apache2/$CLEARINGHOUSE
mkdir -p /var/log/apache2/$OPTIN_MANAGER
chmod o-w /var/log/apache2/$CLEARINGHOUSE
chmod o-w /var/log/apache2/$OPTIN_MANAGER

# Enable various Apache flags
a2enmod wsgi
a2enmod ssl
a2enmod macro
a2enflag SSL

# Generate server certificates
/usr/bin/gensslcert

# restart apache
/etc/init.d/apache2 restart

