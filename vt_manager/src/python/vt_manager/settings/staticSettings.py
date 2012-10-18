'''
<<<<<<< HEAD
	@author: msune

	Ofelia VT AM settings file (Static settings) 
'''

=======
Ofelia VT AM settings file (static settings)

@author: msune, CarolinaFernandez
'''

#
# Based upon the Apache server configuration files.
#

### Section 1: VT AM settings
#
# Static settings for Virtual Machine Aggregate Manager.
#

>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
import sys, traceback, logging
from django.conf import settings
from os.path import dirname, join

<<<<<<< HEAD

#EMAIL_HOST = "smtp.gmail.com"
=======
#
# Email configuration.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
DEFAULT_FROM_EMAIL = "OFELIA-noreply@fp7-ofelia.eu"
EMAIL_USE_TLS=True
EMAIL_HOST='mail.eict.fp7-ofelia.eu'
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_PORT=25 

<<<<<<< HEAD
# Enable debugging?
DEBUG = True


##### Advanced parameters: you shouldn't be changing them, unless you have a good reason #########

#SRC_DIR
SRC_DIR = join(dirname(__file__), '../../../')

#Database default params
=======
#
# Set true to enable debug.
#
DEBUG = True

##
## Advanced parameters.
## You SHOULD NOT change them unless you have a good reason.
##

#
# Directory for the VT manager sources.
#
SRC_DIR = join(dirname(__file__), '../../../')

#
# Database default parameters.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
DATABASE_ENGINE = 'mysql'
DATABASE_HOST = ''
DATABASE_PORT = ''

<<<<<<< HEAD
# List of callables that know how to import templates from various sources.
=======
#
# List of callables that know how to import templates from various sources.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

<<<<<<< HEAD
#Middleware
=======
#
# Middleware classes for Django.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
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
<<<<<<< HEAD
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
=======

#
# Authentication_backend(s) for Django.
# django.contrib.auth.backends.RemoteUserBackend: added for HTTPS over
# RPC following http://packages.python.org/rpc4django/usage/auth.html
#
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'vt_manager.common.backends.remoteuser.NoCreateRemoteUserBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

#
# Path to the urls.py file.
#
ROOT_URLCONF = 'vt_manager.urls'

#
# Path to the template (.html files) folder(s).
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
TEMPLATE_DIRS = (
    join(SRC_DIR, 'python/vt_manager/views/templates/default'),
)

<<<<<<< HEAD
#THEME_DIR = join(SRC_DIR, 'python/vt_manager/views/static/media')

=======
#
# Template context processors
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'vt_manager.common.utils.context_processors.contextSettingsInTemplate',
]

<<<<<<< HEAD
#Static file paths
=======
#
# Path to the static content (images, css, js) folders.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
MEDIA_ROOT = join(SRC_DIR+"python/vt_manager/views/static/", "media")
MEDIA_URL = '/static/media'
ADMIN_MEDIA_PREFIX = '/admin/media/'

<<<<<<< HEAD
#Installed apps
=======
#
# Installed apps
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
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
    'pypelib.persistence.backends.django',
<<<<<<< HEAD
#    'vt_manager.communication',
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
=======
)

#
# URL to redirect after login.
#
LOGIN_REDIRECT_URL = '/'

#
# Registration application settings.
#
ACCOUNT_ACTIVATION_DAYS = 3

#
# See Django documentation.
#
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = True

#
# Set session cookie names so as to avoid conflicts.
#
SESSION_COOKIE_NAME = "vtam_sessionid"

#
# Workaround to allow test:// schemes.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

<<<<<<< HEAD
#DJANGO id
SITE_ID = 1

# default sitename
SITE_NAME = 'OFELIA CF VT Manager' #'Opt-In Manager'

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

=======
#
# Django ID.
#
SITE_ID = 1

#
# Default sitename.
#
SITE_NAME = 'OFELIA CF VT Manager'

#
# Fully qualified name
#
SITE_DOMAIN = 'expedient.site:8445'

#
# Basic authentication urls
#
BASIC_AUTH_URLS = (
    r'^/xmlrpc/.*',
)

#
# List of locations that do not need authentication to access.
#
SITE_LOCKDOWN_EXCEPTIONS = (
    r'^/accounts/register/.*$',
    r'^/accounts/activate/.*$',
    r'^/img/.*',
    r'^/css/.*',
    r'^/static/media/.*',
)

#
# Set to force https.
#
DOMAIN_SCHEME = "https"

#
# Agent monitoring interval in seconds. That is, seconds until it
# asks for the current status of the servers and virtual machines.
#
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
MONITORING_INTERVAL = 45

