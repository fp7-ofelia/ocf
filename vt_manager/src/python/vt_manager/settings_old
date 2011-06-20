'''
    Settings
    author: @msune
'''
import sys, traceback, logging
from django.conf import settings
from os.path import dirname, join



##### Basic parameters: you might want to change them #########


ROOT_USERNAME = "expedient"
ROOT_PASSWORD = "expedient"
ROOT_EMAIL    = "i2catopenflow@gmail.com"
VTAM_URL      = "147.83.206.92:8445/xmlrpc/agent"
ISLAND_IP_RANGE = "10.216.12.0"
ISLAND_NETMASK = "255.255.252.0"
ISLAND_GW = "192.168.10.1"
ISLAND_DNS1 = "84.88.39.235"
ISLAND_DNS2 = ""

ADMINS = [
    ("expedient", ROOT_EMAIL),
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
SITE_DOMAIN = "OfeliaSDKR1"

SITE_IP_ADDR = "192.168.254.193"
MININET_VMS = [
    ("84.88.41.12", 22),
]

#Database params
DATABASE_NAME = "vtm"
DATABASE_USER = "expedient"
DATABASE_PASSWORD = "expedient"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2f(jw$r445m^g3#1e)mysi2c#4ny83*4al=#adkj1o98ic+44i'

# Enable debugging?
DEBUG = True




##### Advanced parameters: you shouldn't be changing them, unless you have a good reason #########

#SRC_DIR
SRC_DIR = join(dirname(__file__), '../../')

#Database default params
DATABASE_ENGINE = 'mysql'
DATABASE_HOST = ''
DATABASE_PORT = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
#Middleware
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'vt_manager.common.middleware.basicauth.HTTPBasicAuthMiddleware',
    'vt_manager.common.middleware.sitelockdown.SiteLockDown',
)
#Authentication_backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'vt_manager.common.backends.remoteuser.NoCreateRemoteUserBackend',
    #VTAM: added for HTTPS over RPC following http://packages.python.org/rpc4django/usage/auth.html
    'django.contrib.auth.backends.RemoteUserBackend',
)

#Urls.py
ROOT_URLCONF = 'vt_manager.urls'

#Template dirs
TEMPLATE_DIRS = (
    join(SRC_DIR, 'python/vt_manager/views/templates'),
)

#Static file paths
MEDIA_ROOT = join(SRC_DIR+"views/static/", "media")
MEDIA_URL = '/static/media'
ADMIN_MEDIA_PREFIX = '/admin/media/'

#Installed apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'vt_manager.common.rpc4django',
    'vt_manager.common.defaultsite',
    'registration',
    'django_evolution',
    'vt_manager.models',
    'vt_manager',
    'vt_manager.communication',
)

#Redirect login
LOGIN_REDIRECT_URL = '/'

# Registration App settings
ACCOUNT_ACTIVATION_DAYS = 3

TEMPLATE_DEBUG = DEBUG
'''See Django documentation.'''

DEBUG_PROPAGATE_EXCEPTIONS = True
'''See Django documentation.'''

## Session cookie names to avoid conflicts
SESSION_COOKIE_NAME = "vtam_sessionid"

## workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

#DJANGO id
SITE_ID = 1

# default sitename
SITE_NAME = 'VT Manager' #'Opt-In Manager'

#Fully qualified name
SITE_DOMAIN = 'expedient.site:8445'

#Basic authentication urls
BASIC_AUTH_URLS = (
    #r'^/.*',
    r'^/xmlrpc/.*',#.*',
    ### for testing
 #   r'^/dummyfv/.*',
)

# List of locations that do not need authentication to access.
SITE_LOCKDOWN_EXCEPTIONS = (
    r'^/accounts/register/.*$',
    r'^/accounts/activate/.*$',
#    r'^/admin/.*',
#    r'^/accounts/password/reset/.*$',
    r'^/img/.*',
    r'^/css/.*',
    r'^/static/media/.*',
#    r'.*/xmlrpc/?',
)

#Force https
DOMAIN_SCHEME = "https"

MONITORING_INTERVAL = 120
