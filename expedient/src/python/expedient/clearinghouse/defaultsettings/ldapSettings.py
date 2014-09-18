'''
Default Email settings

Created on Aug 18, 2010

@author: dcolle, msune, CarolinaFernandez
'''

#
# Based upon the Apache server configuration files.
#

### Section 1: LDAP Client settings
#
# Default settings for the LDAP server.
#

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType
from settings import CONF_DIR
from settings import AUTH_LDAP_BIND_PASSWORD, AUTH_LDAP_BIND_DN

##
## LDAP CLient settings. Read access only; should point to the slave 
##

#
# URI for the LDAP server to check the clearances.
#
AUTH_LDAP_SERVER_URI = "ldap://ldap.ibbt.fp7-ofelia.eu:389"

#
# Object that locates a user with the given certificate information
# (e.g. "ou=users,dc=userToSearchFor,dc=com")
#
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=fp7-ofelia,dc=eu",ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

#
# Populates the Django user from the LDAP directory.
#
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

#
# Activates the automatic update for all mapped user fields every
# time the user logs in. The default is True (automatic update).
#
AUTH_LDAP_ALWAYS_UPDATE_USER = True

#
# Uses LDAP group membership to calculate group permissions.
#
AUTH_LDAP_FIND_GROUP_PERMS = False

#
# Cache group memberships for an hour to minimize LDAP traffic.
#
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


# -----------------------------------------------------------------
# LDAP CLient settings to MASTER for write access
# -----------------------------------------------------------------

#
# URI for the master LDAP server to check the clearances.
# Do NEVER use a slave LDAP server here.
#
LDAP_MASTER_URI="ldap://ldap.ibbt.fp7-ofelia.eu"

#
# Use unversioned password
#
LDAP_MASTER_DN=AUTH_LDAP_BIND_DN
LDAP_MASTER_PWD=AUTH_LDAP_BIND_PASSWORD

###############################################################################
# TODO: Explain the following
###############################################################################

LDAP_MASTER_SSLDIR="%s/ldap.ssl" % CONF_DIR
LDAP_MASTER_CA="%s/ca.crt" % LDAP_MASTER_SSLDIR
LDAP_MASTER_CERT="%s/expedientldap.crt" % LDAP_MASTER_SSLDIR
LDAP_MASTER_KEY="%s/expedientldap.key" % LDAP_MASTER_SSLDIR
LDAP_MASTER_REQCERT=ldap.OPT_X_TLS_DEMAND
LDAP_MASTER_TIMEOUT=15

#
# See LdapProxy.create_or_update
#
LDAP_MASTER_RETRIES=3

#
# Leave possibility to continue locally BUT in an OUT-OF_SYNC mode
# in case e.g. connectivity with central master LDAP server is lost.
#
LDAP_MASTER_DISABLE=False

###############################################################################
# TODO: Explain the following
###############################################################################

LDAP_MASTER_BASE="dc=fp7-ofelia,dc=eu"
LDAP_MASTER_NETGROUPS="ou=netgroups,%s" % LDAP_MASTER_BASE
LDAP_MASTER_USERNETGROUPS="ou=users,%s" % LDAP_MASTER_NETGROUPS
LDAP_MASTER_HOSTNETGROUPS="ou=hosts,%s" % LDAP_MASTER_NETGROUPS

#
# If True, each connection to the LDAP server will call start_tls to
# enable TLS encryption over the standard LDAP port.
#
AUTH_LDAP_START_TLS = True

LDAP_STORE_PROJECTS=True

#
# Dictionary of options to pass to python-ldap via ldap.set_option()
# Keys are ldap.OPT_* constants.
#
# There are a number of configuration options that can be given that
# affect the TLS connection. For example, ldap.OPT_X_TLS_REQUIRE_CERT
# can be set to ldap.OPT_X_TLS_NEVER to disable certificate verification,
# perhaps to allow self-signed certificates.
#
AUTH_LDAP_GLOBAL_OPTIONS = {
	ldap.OPT_X_TLS_CACERTFILE: LDAP_MASTER_CA,
	ldap.OPT_X_TLS_REQUIRE_CERT: LDAP_MASTER_REQCERT,
	ldap.OPT_TIMEOUT: LDAP_MASTER_TIMEOUT,
}
