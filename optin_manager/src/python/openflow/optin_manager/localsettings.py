CONF_DIR = '/home/user/ofelia-git/optin_manager/src/python/openflow/optin_manager' #'/etc/optin_manager'
SRC_DIR = '/home/user/ofelia-git/optin_manager/src' #'/usr/share/optin_manager'

ROOT_USERNAME = "expedient"
ROOT_PASSWORD = "expedient"
ROOT_EMAIL    = "i2catopenflow@gmail.com"

ADMINS = [
    ("expedient", ROOT_EMAIL),
]

MANAGERS = ADMINS

EMAIL_HOST = "smtp.gmail.com"
DEFAULT_FROM_EMAIL = "no-reply@gmail.com"

#SITE_DOMAIN = "expedient.r1"
SITE_DOMAIN = "OfeliaSDKR1"

SITE_IP_ADDR = "192.168.254.193"
MININET_VMS = [
    ("84.88.41.12", 22),
]

DATABASE_USER = "expedient"
DATABASE_PASSWORD = "expedient"
