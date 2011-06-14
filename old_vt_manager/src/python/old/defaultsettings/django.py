'''
Created on Sep 2, 2010

@author: Peyman Kazemian
'''
# Django settings for OM project.
from os.path import dirname, join
import os
import pkg_resources
import sys

try:
    print sys.path
    from vt_manager.localsettings import SRC_DIR as location
except ImportError:
    pass
   # location = pkg_resources.resource_filename(
        #pkg_resources.Requirement.parse("optin_manager"), "")
        #pkg_resources.Requirement.parse("vt_manager"), "")
    # TODO: Hack!
    #if location.endswith("src/python"):
    #    location = location[:-7]
    #else:
    #    location = location + "/share/vt_manager"
    location="/home/user/ofelia-git/vt_manager/src/python"        

SRC_DIR = location
'''Base location of non-python source files.'''

try:
    from localsettings import CONF_DIR as location
except ImportError:
    # TODO: Hack!
    location = "/etc/optin_manager"
    location = "/home/user/ofelia-git/vt_manager/src/python/vt_manager"
        
CONF_DIR = location
'''Location of local Expedient configuration files.

Example: /etc/optin_manager/

'''

#STATIC_DOC_ROOT = join(SRC_DIR,"static/vt_manager")
STATIC_DOC_ROOT = join(SRC_DIR,"python/vt_manager/views/static")


TIME_ZONE = 'America/Los_Angeles'
'''Local time zone for this installation.

Choices can be found here:
http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
although not all choices may be available on all operating systems.
If running in a Windows environment this must be set to the same as your
system time zone.

'''

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
#MEDIA_URL = '/static/media'
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
    'common.middleware.basicauth.HTTPBasicAuthMiddleware',
    'common.middleware.sitelockdown.SiteLockDown',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'common.backends.remoteuser.NoCreateRemoteUserBackend',
    #VTAM: added for HTTPS over RPC following http://packages.python.org/rpc4django/usage/auth.html
    'django.contrib.auth.backends.RemoteUserBackend',
)

ROOT_URLCONF = 'vt_manager.urls'

TEMPLATE_DIRS = (
    join(SRC_DIR, 'templates'),
    join(SRC_DIR, 'templates/vt_manager'),
    join(SRC_DIR, 'python/vt_manager/views/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'common.rpc4django',
    'common.defaultsite',
    'registration',
    'django_evolution',
    'vt_manager.models',
    'vt_manager',
    'vt_manager.communication',
)


LOGIN_REDIRECT_URL = '/'

# Registration App settings
ACCOUNT_ACTIVATION_DAYS = 3

# Enable debugging?
DEBUG = True
'''Enable/Disable debugging mode. See Django docs on this setting.'''

TEMPLATE_DEBUG = DEBUG
'''See Django documentation.'''

DEBUG_PROPAGATE_EXCEPTIONS = True
'''See Django documentation.'''

# Session cookie names to avoid conflicts
SESSION_COOKIE_NAME = "vtam_sessionid"

# workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")
