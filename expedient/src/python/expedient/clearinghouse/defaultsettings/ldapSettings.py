'''Default Email settings

Created on Aug 18, 2010

@author: dcolle,msune
'''


import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType
from localsettings import CONF_DIR
from localsettings import AUTH_LDAP_BIND_PASSWORD
######################################################################
#LDAP CLient settings; only for read access;should point to the slave 
######################################################################


# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://ldap.ibbt.fp7-ofelia.eu:389"

AUTH_LDAP_BIND_DN = "cn=admin,dc=fp7-ofelia,dc=eu"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=fp7-ofelia,dc=eu",ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# or perhaps:
# AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

# Set up the basic group parameters.
#AUTH_LDAP_GROUP_SEARCH = LDAPSearch("cn=i2cat,ou=groups,dc=fp7-ofelia,dc=eu",
#    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
#)
#AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType(name_attr="cn")

# Only users in this group can log in.
#AUTH_LDAP_REQUIRE_GROUP = "cn=i2cat,ou=groups,dc=fp7-ofelia,dc=eu"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

#AUTH_LDAP_PROFILE_ATTR_MAP = {
#    "employee_number": "employeeNumber"
#}

#AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
#    "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
#    "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com"
#}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
#AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_FIND_GROUP_PERMS = False

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

######################################################################


######################################################################
#LDAP CLient settings to MASTER for write access
######################################################################

 
# THIS SHOULD BE ALWAYS THE MASTER, NEVER A SLAVE LDAP SERVER
#LDAP_MASTER_URI="ldap://ldap.ibbt.fp7-ofelia.eu"
LDAP_MASTER_URI="ldap://ldap.ibbt.fp7-ofelia.eu"
LDAP_MASTER_DN="cn=admin,dc=fp7-ofelia,dc=eu"
LDAP_MASTER_PWD="ailefo"
LDAP_MASTER_SSLDIR="%s/ldap.ssl" % CONF_DIR
LDAP_MASTER_CA="%s/ca.crt" % LDAP_MASTER_SSLDIR
LDAP_MASTER_CERT="%s/expedientldap.crt" % LDAP_MASTER_SSLDIR
LDAP_MASTER_KEY="%s/expedientldap.key" % LDAP_MASTER_SSLDIR
LDAP_MASTER_REQCERT=ldap.OPT_X_TLS_NEVER
LDAP_MASTER_TIMEOUT=15
#LDAP_MASTER_EXPEDIENT_DISCR="ibbt" # to make sure that names (e.g. of netgroups) are unique across different islands
LDAP_MASTER_RETRIES=3 # see LdapProxy.create_or_update
LDAP_MASTER_DISABLE=False # For example, in case connectivity with central master LDAP server is lost, leave possibility to continue locally BUT IN AN OUT-OF_SYNC MODE.

LDAP_MASTER_BASE="dc=fp7-ofelia,dc=eu"
LDAP_MASTER_NETGROUPS="ou=netgroups,%s" % LDAP_MASTER_BASE
LDAP_MASTER_USERNETGROUPS="ou=users,%s" % LDAP_MASTER_NETGROUPS
LDAP_MASTER_HOSTNETGROUPS="ou=hosts,%s" % LDAP_MASTER_NETGROUPS

LDAP_STORE_PROJECTS=True
