'''
@author: jnaous
'''
# Django settings for clearinghouse project.
from os.path import dirname, join

SRC_DIR = join(dirname(__file__), '../../../')

# For serving static content - dev version only
STATIC_DOC_ROOT = join(SRC_DIR, 'static/expedient/clearinghouse')

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = join(SRC_DIR, '../db/expedient/clearinghouse/clearinghouse.db') # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join(STATIC_DOC_ROOT, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6=egu-&rx7a+h%yjlt=lny=s+uz0$a_p8je=3q!+-^4w^zxkb8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'expedient.common.middleware.basicauth.HTTPBasicAuthMiddleware',
    'expedient.common.middleware.sitelockdown.SiteLockDown',
    'expedient.common.permissions.middleware.PermissionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'expedient.common.backends.remoteuser.NoCreateRemoteUserBackend',
)

ROOT_URLCONF = 'expedient.clearinghouse.urls'

TEMPLATE_DIRS = (
    join(SRC_DIR, 'templates'),
    join(SRC_DIR, 'templates/expedient/clearinghouse'),
    join(SRC_DIR, 'templates/expedient/common'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'autoslug',
    'registration',
    'expedient.common.permissions',
    'expedient.common.breadcrumbs',
    'expedient.common.rpc4django',
    'expedient.common.utils',
    'expedient.common.extendable',
    'expedient.common.xmlrpc_serverproxy',
    'expedient.common.messaging',
    'expedient.common.defaultsite',
    'expedient.clearinghouse.aggregate',
    'expedient.clearinghouse.project',
    'expedient.clearinghouse.resources',
    'expedient.clearinghouse.slice',
    'expedient.clearinghouse.users',
    'openflow.plugin',
    'geni',
    'geni.planetlab',
    'expedient.ui.html',
###### For Testing #######################
    'openflow.dummyom',
)

LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "users.UserProfile"

DEFAULT_FROM_EMAIL = 'no-reply@geni.org'
EMAIL_SUBJECT_PREFIX = '[GENI-Clearinghouse] '

# Registration App settings
ACCOUNT_ACTIVATION_DAYS = 3

# XML-RPC settings
XMLRPC_TRUSTED_CA_PATH = join(SRC_DIR, '../ssl.crt')
XMLRPC_TIMEOUT = 120
MY_CA = join(XMLRPC_TRUSTED_CA_PATH, 'ca.crt')

# default site
SITE_ID = 1
SITE_NAME = "Expedient Clearinghouse"
SITE_DOMAIN = "clearinghouse.geni.org"

# Messaging settings
NUM_LATEST_MSGS = 10
NUM_CONTEXT_MSGS = 3

# Aggregate app settings
AGGREGATE_LOGOS_DIR = "aggregate_logos/"

# Openflow GAPI settings
OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+openflow:stanford"
OPENFLOW_GAPI_AM_URN = "urn:publicid:IDN+openflow:stanford+am+authority"

DEBUG = True

# For Testing
# URLs that accept HTTP Basic Authentication.
BASIC_AUTH_URLS = (
    r'^/dummyom/.*',
)

# List of locations that do not need authentication to access.
SITE_LOCKDOWN_EXCEPTIONS = (
    r'^/accounts/register/.*$',
    r'^/accounts/activate/.*$',
    r'^/admin/.*',
    r'^/accounts/password/reset/.*$',
    r'^/img/.*',
    r'^/css/.*',
    r'^/static/media/.*',
    r'.*/xmlrpc/?',
    r'.*/gapi/?',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'expedient.common.messaging.context_processors.messaging',
)

# Installed UI Plugins
UI_PLUGINS = (
    ('expedient.ui.html.plugin', 'html_ui', 'expedient.ui.html.urls'),
)

# Installed Aggregate Models
AGGREGATE_PLUGINS = (
    ('openflow.plugin.models.OpenFlowAggregate'),
    ('geni.planetlab.models.PlanetLabAggregate'),
)

# What is the scheme to use when sending urls? 
DOMAIN_SCHEME = "https"

# Location of GENI x509 certs and keys
GCF_X509_CERT_DIR = join(SRC_DIR, "../gcf-x509.crt")
GCF_X509_KEY_DIR = join(SRC_DIR, "../gcf-x509.key")
GCF_X509_CRED_DIR = join(SRC_DIR, "../gcf-x509.cred")
GCF_X509_CH_CERT = join(GCF_X509_CERT_DIR, "ch.crt")
GCF_X509_CH_KEY = join(GCF_X509_KEY_DIR, "ch.crt")
GCF_X509_CA_CERT = join(GCF_X509_CERT_DIR, "ca.crt")
GCF_X509_CA_KEY = join(GCF_X509_KEY_DIR, "ca.crt")
GCF_NULL_SLICE_CRED = join(GCF_X509_CRED_DIR, "ch.cred")
GCF_URN_PREFIX = "expedient:stanford"

# get custom install info
from deployment_settings import *

TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS

# Session cookie names to avoid conflicts
SESSION_COOKIE_NAME = "ch_sessionid"

# workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

# Logging
from expedient.common import loggingconf
import logging
if DEBUG:
    loggingconf.set_up(logging.DEBUG)
else:
    loggingconf.set_up(logging.INFO)
