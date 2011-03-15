CONF_DIR = '/opt/ofelia/expedient/src/python/expedient/clearinghouse'
SRC_DIR = '/opt/ofelia/expedient/src'


ROOT_USERNAME = "expedient"
ROOT_PASSWORD = "expedient"
ROOT_EMAIL    = "i2catopenflow@gmail.com"

ADMINS = [
    ("i2cat OFELIA Admin", ROOT_EMAIL),
]

MANAGERS = ADMINS

EMAIL_HOST = "smtp.gmail.com"
DEFAULT_FROM_EMAIL = "no-reply@gmail.com"

GCF_BASE_NAME = "expedient//i2CAT"
GCF_URN_PREFIX = "expedient:i2CAT"

SITE_DOMAIN = "Expedient"

OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+expedient:i2CAT:openflow"
OPENFLOW_GAPI_AM_URN = OPENFLOW_GAPI_RSC_URN_PREFIX+"+am"

SITE_IP_ADDR = "172.16.1.150"
MININET_VMS = [
    ("84.88.41.12", 22),
]

DATABASE_USER = "control"
DATABASE_PASSWORD = "982jkewHFHdfbk429fr"
DATABASE_HOST = "172.16.1.151"
DATABASE_NAME = "expedient743754"
                         

