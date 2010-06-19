'''
@author: jnaous
'''
from os.path import join

DEBUG = True
ADMINS = (
    ('<your name>', '<your email>'),
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6=egu-&rx7a+h%yjlt=lny=s+uz0$a_p8je=3q!+-^4w^zxkb8'

# E-Mail sending settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'clearinghouse.geni@gmail.com'
EMAIL_HOST_PASSWORD = "the password" # example
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'no-reply@geni.org'
EMAIL_SUBJECT_PREFIX = '[GENI-Clearinghouse] '

# XML-RPC settings
XMLRPC_TRUSTED_CA_PATH = '/etc/apache2/ssl.crt'
XMLRPC_TIMEOUT = 120
MY_CA = join(XMLRPC_TRUSTED_CA_PATH, 'ca.crt')

# default site
SITE_NAME = "Expedient Clearinghouse"
SITE_DOMAIN = "clearinghouse.geni.org" # example

# Openflow GAPI settings
OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+openflow:stanford"
OPENFLOW_GAPI_AM_URN = "urn:publicid:IDN+openflow:stanford+am+authority"
