'''General Django settings.

@author: jnaous
'''
# Django settings for Expedient project.
import os
import sys
import pkg_resources
from utils import append_to_local_setting
import ldap

sys.path.append(os.path.dirname(__file__)+'/../../../../../../vt_manager/src/python')
#sys.path.append(os.path.dirname(__file__)+'/../../../plugins')

try:
    from localsettings import SRC_DIR as location
    sys.path.append(location)
except ImportError:
    try:
        location = os.path.abspath(pkg_resources.resource_filename(
            pkg_resources.Requirement.parse("expedient"), ""))
    except pkg_resources.DistributionNotFound:
        location = os.path.abspath(
            pkg_resources.resource_filename("expedient", ".."))
    # TODO: Hack!
    if location.endswith("src/python"):
        location = location[:-7]
    else:
        location = location + "/share/expedient"

SRC_DIR = location
'''Base location of non-python source files.'''

try:
    from localsettings import CONF_DIR as location
except ImportError:
    # TODO: Hack!
    location = "/etc/expedient"

CONF_DIR = location
'''Location of local Expedient configuration files.

Example: /etc/expedient/

'''

try:
    from localsettings import STATIC_DOC_ROOT as location
except ImportError:
    location = os.path.join(SRC_DIR, "static", "expedient", "clearinghouse")

STATIC_DOC_ROOT = location
'''Location of static content.

Example: /srv/www/expedient/

'''

TIME_ZONE = 'America/Los_Angeles'
'''Local time zone for this installation.

Choices can be found here:
http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
although not all choices may be available on all operating systems.
If running in a Windows environment this must be set to the same as your
system time zone.

'''

LANGUAGE_CODE = 'en-us'
'''Language code for this installation. All choices can be found here:
http://www.i18nguy.com/unicode/language-identifiers.html'''

USE_I18N = False
'''If you set this to False, Django will make some optimizations so as not
to load the internationalization machinery.'''

try:
    from localsettings import *
except ImportError:
    pass

MEDIA_ROOT = os.path.join(STATIC_DOC_ROOT, "media")
'''Absolute path to the directory that holds media.
Example: "/home/media/media.lawrence.com/"'''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/media/default'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

SECRET_KEY = '6=egu-&rx7a+h%yjlt=lny=s+uz0$a_p8je=3q!+-^4w^zxkb8'
'''Make this unique, and don't share it with anybody.

This needs to be overridden.

'''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
]
append_to_local_setting(
    "TEMPLATE_LOADERS", TEMPLATE_LOADERS, globals())

MIDDLEWARE_CLASSES = [
#    'expedient.common.middleware.exceptionprinter.ExceptionPrinter',
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
    'expedient_geni.middleware.CreateUserGID',
]
append_to_local_setting(
    "MIDDLEWARE_CLASSES", MIDDLEWARE_CLASSES, globals(), at_start=True,
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'expedient_geni.backends.GENIRemoteUserBackend',
]
if ENABLE_LDAP_BACKEND:
    AUTHENTICATION_BACKENDS.insert(1,'django_auth_ldap.backend.LDAPBackend')

append_to_local_setting(
    "AUTHENTICATION_BACKENDS", AUTHENTICATION_BACKENDS, globals(),
)
  
ROOT_URLCONF = 'expedient.clearinghouse.urls'

TEMPLATE_DIRS = [
    os.path.join(SRC_DIR, 'templates/default'),
    os.path.join(SRC_DIR, 'templates/default/expedient/clearinghouse'),
    os.path.join(SRC_DIR, 'templates/default/expedient/common'),
##    os.path.join(SRC_DIR, 'python/vt_plugin/views/templates/default'),
]
append_to_local_setting(
    "TEMPLATE_DIRS", TEMPLATE_DIRS, globals(),
)


INSTALLED_APPS = [
    'expedient.clearinghouse.firstapp', # Must remain first!
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'autoslug',
    'registration',
    'django_evolution',
    'expedient.common.timer',
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
#    'openflow.plugin',
    'expedient_geni',
    'expedient_geni.planetlab',
    'expedient_geni.gopenflow',
#    'expedient.ui.html',
    'expedient.ui.rspec',
#    'vt_plugin',
#    'vt_plugin.communication',
#    'openflow.dummyom',
#    'sample_resource',
]
append_to_local_setting(
    "INSTALLED_APPS", INSTALLED_APPS, globals(), at_start=True,
)

LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "users.UserProfile"

ACCOUNT_ACTIVATION_DAYS = 3
'''Number of days account activation links are valid.'''

AGGREGATE_LOGOS_DIR = "aggregate_logos/"
'''Directory relative to MEDIA_ROOT where all aggregate logos are uploaded.'''

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'expedient.common.messaging.context_processors.messaging',
    'expedient.common.utils.context_processors.contextSettingsInTemplate',
]
append_to_local_setting(
    "TEMPLATE_CONTEXT_PROCESSORS", TEMPLATE_CONTEXT_PROCESSORS, globals())
'''See Django documentation.'''

# Enable debugging?
DEBUG = True
'''Enable/Disable debugging mode. See Django docs on this setting.'''

try:
    from localsettings import *
except ImportError:
    pass

TEMPLATE_DEBUG = DEBUG
'''See Django documentation.'''

DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
'''See Django documentation.'''

SESSION_COOKIE_NAME = "ch_sessionid"
'''Session cookie names to avoid cookie name conflicts.'''

# workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

