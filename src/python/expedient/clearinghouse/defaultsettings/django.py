'''General Django settings.

@author: jnaous
'''
# Django settings for clearinghouse project.
from os.path import dirname, join

SRC_DIR = join(dirname(__file__), '../../../../')
PROJ_DIR = join(dirname(__file__), '../')

# For serving static content - dev version only
STATIC_DOC_ROOT = join(SRC_DIR, 'static/expedient/clearinghouse')

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
MEDIA_URL = '/static/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

SECRET_KEY = '6=egu-&rx7a+h%yjlt=lny=s+uz0$a_p8je=3q!+-^4w^zxkb8'
'''Make this unique, and don't share it with anybody.

This needs to be overridden.

'''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'expedient.common.middleware.exceptionprinter.ExceptionPrinter',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'expedient.common.middleware.basicauth.HTTPBasicAuthMiddleware',
    'expedient.common.middleware.sitelockdown.SiteLockDown',
    'expedient.common.middleware.threadlocals.ThreadLocals',
    'expedient.common.permissions.middleware.PermissionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'geni.backends.GENIRemoteUserBackend',
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
    'django_evolution',
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
    'expedient.clearinghouse.commands',
    'expedient.clearinghouse.aggregate',
    'expedient.clearinghouse.roles',
    'expedient.clearinghouse.project',
    'expedient.clearinghouse.resources',
    'expedient.clearinghouse.slice',
    'expedient.clearinghouse.users',
    'expedient.clearinghouse.permissionmgmt',
    'openflow.plugin',
    'geni',
    'geni.planetlab',
    'expedient.ui.html',
###### For Testing #######################
    'openflow.dummyom',
)

LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "users.UserProfile"

ACCOUNT_ACTIVATION_DAYS = 3
'''Number of days account activation links are valid.'''

AGGREGATE_LOGOS_DIR = "aggregate_logos/"
'''Directory relative to MEDIA_ROOT where all aggregate logos are uploaded.'''

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'expedient.common.messaging.context_processors.messaging',
)
'''See Django documentation.'''

# Enable debugging?
DEBUG = True
'''Enable/Disable debugging mode. See Django docs on this setting.'''

TEMPLATE_DEBUG = DEBUG
'''See Django documentation.'''

DEBUG_PROPAGATE_EXCEPTIONS = True
'''See Django documentation.'''

SESSION_COOKIE_NAME = "ch_sessionid"
'''Session cookie names to avoid cookie name conflicts.'''

# workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

