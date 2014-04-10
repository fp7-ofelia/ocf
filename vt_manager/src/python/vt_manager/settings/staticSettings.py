'''
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

import sys, traceback, logging
from django.conf import settings
from os.path import dirname, join

#
# Email configuration.
#
DEFAULT_FROM_EMAIL = "OFELIA-noreply@fp7-ofelia.eu"
EMAIL_SUBJECT_PREFIX = '[OFELIA CF] '
EMAIL_USE_TLS=True
EMAIL_HOST='mail.eict.fp7-ofelia.eu'
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_PORT=25 

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
#SRC_DIR = join(dirname(__file__), '../../../')
SRC_DIR = "/opt/ofelia/vt_manager/src/"

#
# Database default parameters.
#
DATABASE_ENGINE = 'mysql'
DATABASE_HOST = ''
DATABASE_PORT = ''

#
# List of callables that know how to import templates from various sources.
#
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

#
# Middleware classes for Django.
#
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'vt_manager.common.middleware.basicauth.HTTPBasicAuthMiddleware',
    'vt_manager.common.middleware.sitelockdown.SiteLockDown',
    'vt_manager.common.middleware.thread_local.threadlocal',
)

#
# Authentication_backend(s) for Django.
# django.contrib.auth.backends.RemoteUserBackend: added for HTTPS over
# RPC following http://packages.python.org/rpc4django/usage/auth.html
#
AUTHENTICATION_BACKENDS = (
    'vt_manager.common.backends.remoteuser.NoCreateRemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
)

#
# Path to the urls.py file.
#
ROOT_URLCONF = 'vt_manager.urls'

#
# Path to the template (.html files) folder(s).
#
TEMPLATE_DIRS = (
    join(SRC_DIR, 'python/vt_manager/views/templates/default'),
)

#
# Template context processors
#
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'vt_manager.common.utils.context_processors.contextSettingsInTemplate',
]

#
# Path to the static content (images, css, js) folders.
#
MEDIA_ROOT = join(SRC_DIR+"python/vt_manager/views/static/", "media")
MEDIA_URL = '/static/media'
ADMIN_MEDIA_PREFIX = '/admin/media/'

#
# Installed apps
#
INSTALLED_APPS = (
    'vt_manager.common.longer_username',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'vt_manager.common.rpc4django',
    'vt_manager.common.defaultsite',
    'vt_manager.common.commands',
    'registration',
    'django_evolution',
    'vt_manager.models',
    'vt_manager',
    'pypelib.persistence.backends.django',
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
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

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
# XXX: This does not seem to "substract" the sites allowed in SITE_LOCKDOWN_EXCEPTIONS,
# under the same path that the ones set here, so better to add here one by one.
BASIC_AUTH_URLS = (
    #r'^/xmlrpc/.*',
    r'^/xmlrpc/?$',
    r'^/xmlrpc/plugin/?$',
    r'^/xmlrpc/agent/?$',
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
    r'^/xmlrpc/sfa/?$',
)

#
# Set to force https.
#
DOMAIN_SCHEME = "https"

#
# Agent monitoring interval in seconds. That is, seconds until it
# asks for the current status of the servers and virtual machines.
#
MONITORING_INTERVAL = 45

