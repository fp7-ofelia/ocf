# Django settings for OM project.
from os.path import dirname, join
import sys

SRC_DIR = join(dirname(__file__), '../../../')
sys.path.append(join(SRC_DIR,'python/'))

STATIC_DOC_ROOT = join(SRC_DIR, 'static/openflow/optin_manager')

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = join(SRC_DIR, '../db/openflow/optin_manager/om.db')  # Or path to database file if using sqlite3.
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
SECRET_KEY = '2f(jw$r445m^g3#1e)mysi2c#4ny83*4al=#adkj1o98ic+44i'

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
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'expedient.common.backends.remoteuser.NoCreateRemoteUserBackend',
)

ROOT_URLCONF = 'openflow.optin_manager.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(SRC_DIR, 'templates'),
    join(SRC_DIR, 'templates/openflow/optin_manager'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'expedient.common.rpc4django',
    'expedient.common.xmlrpc_serverproxy',
    'expedient.common.defaultsite',
    'registration',
    'openflow.optin_manager.users',
    'openflow.optin_manager.flowspace',
    'openflow.optin_manager.opts',
    'openflow.optin_manager.admin_manager',
    'openflow.optin_manager.xmlrpc_server',
    'openflow.optin_manager.controls',
###### For Testing #######################
    'openflow.optin_manager.dummyfv',
)

AUTH_PROFILE_MODULE = "users.UserProfile"

LOGIN_REDIRECT_URL = '/'

# E-Mail sending settings
DEFAULT_FROM_EMAIL = 'no-reply@stanford.edu'
EMAIL_SUBJECT_PREFIX = '[GENI-Opt IN Manager]'

# Registration App settings
ACCOUNT_ACTIVATION_DAYS = 3

# XML-RPC settings
XMLRPC_TRUSTED_CA_PATH = join(SRC_DIR, '../ssl.crt')
XMLRPC_TIMEOUT = 120
MY_CA = join(XMLRPC_TRUSTED_CA_PATH, 'ca.crt')

# default site
SITE_ID = 1

DOMAIN_SCHEME = "https"


DEBUG = True

BASIC_AUTH_URLS = (
    r'^/xmlrpc/xmlrpc.*',
    ### for testing
    r'^/dummyfv/.*',
)


# Session cookie names to avoid conflicts
SESSION_COOKIE_NAME = "om_sessionid"

# workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

# get custom install info
from deployment_settings import *

TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS

# Logging
from expedient.common import loggingconf
import logging
if DEBUG:
    loggingconf.set_up(logging.DEBUG)
else:
    loggingconf.set_up(logging.INFO)
