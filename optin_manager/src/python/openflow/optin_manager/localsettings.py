CONF_DIR = '/opt/ofelia/optin_manager/src/python/openflow/optin_manager' #'/etc/optin_manager'
SRC_DIR = '/opt/ofelia/optin_manager/src' #'/usr/share/optin_manager'

ROOT_USERNAME = "expedient"
ROOT_PASSWORD = "expedient"
ROOT_EMAIL    = "i2catopenflow@gmail.com"

ADMINS = [
    ("i2cat OFELIA Admin", ROOT_EMAIL),
]

MANAGERS = ADMINS

#EMAIL_HOST = "smtp.gmail.com"
DEFAULT_FROM_EMAIL = "no-reply@gmail.com"
EMAIL_USE_TLS=True
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER='i2catopenflow@gmail.com'
EMAIL_HOST_PASSWORD="expedient"
EMAIL_PORT=587 

#SITE_DOMAIN = "expedient.r1"
SITE_DOMAIN = "Expedient"

SITE_IP_ADDR = "172.16.1.150"
MININET_VMS = [
    ("84.88.41.12", 22),
]

DATABASE_USER = "control"
DATABASE_PASSWORD = "982jkewHFHdfbk429fr"
DATABASE_HOST = "172.16.1.151"
DATABASE_NAME = "optin8746756"
