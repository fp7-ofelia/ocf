'''
@author: jnaous
'''
from os.path import join

DEBUG = True
ADMINS = (
    ('Jad Naous', 'jnaous@stanford.edu'),
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# E-Mail sending settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'clearinghouse.geni@gmail.com'
EMAIL_HOST_PASSWORD = "OpenF1owRu!z"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'no-reply@geni.org'
EMAIL_SUBJECT_PREFIX = '[GENI-Clearinghouse] '

# XML-RPC settings
MY_CA = '/etc/apache2/ssl.crt/ca.crt'

# default site
SITE_NAME = "Expedient Clearinghouse"
SITE_DOMAIN = "beirut.stanford.edu"

# Openflow GAPI settings
OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+openflow:stanford"
OPENFLOW_GAPI_AM_URN = "urn:publicid:IDN+openflow:stanford+am+authority"

DOMAIN_SCHEME = "https"

from secret_key import SECRET_KEY
