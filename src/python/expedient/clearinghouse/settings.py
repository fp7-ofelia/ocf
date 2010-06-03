'''
@author: jnaous
'''
# Django settings for clearinghouse project.
from os.path import dirname, join

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jad Naous', 'jnaous@stanford.edu'),
)

SRC_DIR = join(dirname(__file__), '../../../')

# For serving static content - dev version only
STATIC_DOC_ROOT = join(SRC_DIR, 'static/expedient/clearinghouse')

MANAGERS = ADMINS

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

SITE_ID = 1

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
    'expedient.clearinghouse.middleware.sitelockdown.SiteLockDown',
)

ROOT_URLCONF = 'expedient.clearinghouse.urls'

TEMPLATE_DIRS = (
    join(SRC_DIR, 'templates'),
    join(SRC_DIR, 'templates/expedient/clearinghouse'),
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
###### For Testing #######################
    'openflow.dummyom',
)

LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "users.UserProfile"

# E-Mail sending settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'clearinghouse.geni@gmail.com'
EMAIL_HOST_PASSWORD = "OpenF1owRu!z"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'no-reply@stanford.edu'
EMAIL_SUBJECT_PREFIX = '[GENI-Clearinghouse] '

# Registration App settings
ACCOUNT_ACTIVATION_DAYS = 3

# XML-RPC settings
XMLRPC_TRUSTED_CA_PATH = '/etc/apache2/ssl.crt'
XMLRPC_TIMEOUT = 120
MY_CA = join(XMLRPC_TRUSTED_CA_PATH, 'ca.crt')

# default site
SITE_ID = 1
SITE_NAME = "Expedient Clearinghouse"
SITE_DOMAIN = "beirut.stanford.edu"

# Messaging settings
NUM_LATEST_MSGS = 10

# Aggregate app settings
AGGREGATE_LOGOS_DIR = "/"

# Openflow GAPI settings
OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+openflow:stanford"
OPENFLOW_GAPI_AM_URN = "urn:publicid:IDN+openflow:stanford+am+authority"

# Logging
from expedient.clearinghouse import loggingconf
import logging
loggingconf.set_up(logging.INFO)
