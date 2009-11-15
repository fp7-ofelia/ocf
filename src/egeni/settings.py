# Django settings for egeni project.
import sys
import os
from os.path import abspath, dirname, join

# Check include paths for a number of modules
SFA_PATH='../../../sfa/'  # Princeton's SFA from http://svn.planet-lab.org/svn/sfa/trunk

sys.path.insert(0, abspath(join(dirname(__file__), SFA_PATH)))
try:
    from sfa.util import soapprotocol 
except ImportError, e:
    sys.stderr.write( "WARNING: Can't find sfa.util from the Princeton SFA package.\n")
    sys.stderr.write( "         This will cause slice management to fail later.\n")

EGENI_DIR = os.path.join(os.path.dirname(__file__), '../..')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# For serving static content - dev version only
STATIC_DOC_ROOT = os.path.join(os.path.dirname(__file__), '../../site_media')


ADMINS = (
    ('Jad Naous', 'jnaous@stanford.edu'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.path.join(EGENI_DIR, 'egeni.db')             # Or path to database file if using sqlite3.
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
MEDIA_ROOT = os.path.join(STATIC_DOC_ROOT, "uploads")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/clearinghouse/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'txv=2bb5j9*#*c=(0w-!$qq9j@nw1dp-+hh1)x$4ebxgsn0mw!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'egeni.sitelockdown.SiteLockDown',
)

ROOT_URLCONF = 'egeni.urls'

TEMPLATE_DIRS = (
    EGENI_DIR + '/django-templates/egeni',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'egeni.clearinghouse'
)

LOGIN_REDIRECT_URL = '/clearinghouse/'

AUTH_PROFILE_MODULE = "clearinghouse.UserProfile"

SFI_CONF_DIR = os.path.join(EGENI_DIR, "cred")
SFI_EXEC_DIR = os.path.join(EGENI_DIR, "src/sfa/client")
