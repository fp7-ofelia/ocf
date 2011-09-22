'''
	@author: msune

	Ofelia VT AM settings file (Static settings) 
'''

import sys, traceback, logging
from django.conf import settings
from os.path import dirname, join



#EMAIL_HOST = "smtp.gmail.com"
DEFAULT_FROM_EMAIL = "no-reply@gmail.com"
EMAIL_USE_TLS=True
EMAIL_HOST='mail.eict.fp7-ofelia.eu'
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_PORT=25 

# Enable debugging?
DEBUG = True


##### Advanced parameters: you shouldn't be changing them, unless you have a good reason #########

#SRC_DIR
SRC_DIR = join(dirname(__file__), '../../../')

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

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'vt_manager.common.utils.context_processors.contextSettingsInTemplate',
]

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

MONITORING_INTERVAL = 45

