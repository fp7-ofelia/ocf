# Django settings for OM project.
from os.path import dirname, join
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
EMAIL_HOST_USER = 'geni.opt.in.manager@gmail.com'
EMAIL_HOST_PASSWORD = "password" # example
EMAIL_PORT = 587

# XML-RPC settings
MY_CA = join('/etc/apache2/ssl.crt', 'ca.crt')

# default site
SITE_NAME = "Expedient Opt-In Manager"
SITE_DOMAIN = "optinmanager.geni.org" # example

DOMAIN_SCHEME = "https"

try:
    from secret_key import SECRET_KEY
except:
    import traceback
    print "Could not import custom secret key because:"
    traceback.print_exc()
    print "Using generic insecure key. Make sure secret_key.py has a SECRET_KEY variable."
