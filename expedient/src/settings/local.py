CONF_DIR = '/opt/ofelia/expedient/src/settings/'
SRC_DIR = '/opt/ofelia/expedient/src'


ROOT_USERNAME = "expedient"
ROOT_PASSWORD = "expedient"
ROOT_EMAIL    = "i2catopenflow@gmail.com"
ISLAND_NAME   = "i2cat"

ADMINS = [
    ("i2cat OFELIA Admin", ROOT_EMAIL),
]

MANAGERS = ADMINS

#SITE_DOMAIN = "192.168.254.193"
SITE_DOMAIN = "192.168.254.176"
#SITE_IP_ADDR = "192.168.254.193"
SITE_IP_ADDR = "192.168.254.176"

DATABASE_USER = "expedient"
DATABASE_PASSWORD = "expedient"

#TO BE MODIFIED ONLY IN DEVELOPMENT ENVIORNMENTS
LDAP_STORE_PROJECTS = False
ALLOW_LOCAL_REGISTRATION=True
AUTH_LDAP_BIND_PASSWORD = "ailefo77917"
AUTH_LDAP_BIND_DN = "uid=i2cat_admin,ou=admins,dc=fp7-ofelia,dc=eu"

#In days
SLICE_DEFAULT_EXPIRATION_TIME = 30

ENABLE_LDAP_BACKEND = True

THEME = "default"
