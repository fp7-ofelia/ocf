'''
@author: jnaous
'''
from os.path import join, dirname

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

# E-Mail sending settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'clearinghouse.geni@gmail.com'
EMAIL_HOST_PASSWORD = "the password" # example
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'no-reply@geni.org'
EMAIL_SUBJECT_PREFIX = '[GENI-Clearinghouse] '

# XML-RPC settings
MY_CA = join('/etc/apache2/ssl.crt/ca.crt')

# default site
SITE_NAME = "Expedient Clearinghouse"
SITE_DOMAIN = "clearinghouse.geni.org" # example

# Openflow GAPI settings
OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+openflow:stanford"
OPENFLOW_GAPI_AM_URN = "urn:publicid:IDN+openflow:stanford+authority+am"
OPENFLOW_GAPI_FILTERED_AGGS = []

# The domain name in URNs for Expedient acting as a Clearinghouse.
# This must not have any spaces or illegal characters
# not allowed in URNs or you will get cryptic errors.
GCF_URN_PREFIX = "expedient:stanford"

DOMAIN_SCHEME = "https"

try:
    from secret_key import SECRET_KEY
except:
    import traceback
    print "Could not import custom secret key because:"
    traceback.print_exc()
    print "Using generic insecure key. Make sure secret_key.py has a SECRET_KEY variable."
