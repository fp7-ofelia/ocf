'''Pull all the default settings and then all overrides.

Created on Aug 19, 2010

@author: jnaous
'''

import os
import sys, traceback

# *Load first* the path variables needed for the stack to run

#CONF_DIR = "/opt/ofelia/expedient/src/python/expedient/clearinghouse"
#CONF_DIR = os.path.join(os.getenv("OCF_PATH"), "expedient/src/python/expedient/clearinghouse")
CONF_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)))
#SRC_DIR = "/opt/ofelia/expedient/src
#SRC_DIR = os.path.join(os.getenv("OCF_PATH"), "expedient/src")
SRC_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../..")

from expedient.clearinghouse.defaultsettings.django import *
from expedient.clearinghouse.defaultsettings.database import *
from expedient.clearinghouse.defaultsettings.admins import *
from expedient.clearinghouse.defaultsettings.email import *
from expedient.clearinghouse.defaultsettings.expedient import *
from expedient.clearinghouse.defaultsettings.logging import *
from expedient.clearinghouse.defaultsettings.gcf import *
from expedient.clearinghouse.defaultsettings.messaging import *
from expedient.clearinghouse.defaultsettings.openflow import *
from expedient.clearinghouse.defaultsettings.site import *
from expedient.clearinghouse.defaultsettings.xmlrpc import *
from expedient.clearinghouse.defaultsettings.openflowtests import *
from expedient.clearinghouse.defaultsettings.tests import *
from expedient.clearinghouse.defaultsettings.ldapSettings import *

# *Before importing plug-in*, load database info
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.%s" % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
    }
}

from expedient.clearinghouse.defaultsettings.plugin import *
# Import the list of required variables
from expedient.clearinghouse.defaultsettings.required import REQUIRED_SETTINGS

# Try getting importing the secret key from a secret_key module
try:
    from secret_key import SECRET_KEY
except ImportError:
    print(
        "Error importing secret_key module. Using default insecure key."
        "Please run the 'create_secret_key' manage.py command to create "
        "a new secret key. Do this only after setting up your local settings."
        " If you are not yet running the production server, you can ignore "
        "this error."
    )

# Now import the local settings
try:
    # do the import here to check that the path exists before doing anything
    from localsettings import *
    
    # Delete all the default required settings
    _modname = globals()['__name__']
    _this_mod = sys.modules[_modname]
    for item in REQUIRED_SETTINGS:
        for var in item[1]:
            delattr(_this_mod, var)

    # now import again to re-insert the deleted settings
    from localsettings import *

    # check that all the required settings are set
    for item in REQUIRED_SETTINGS:
        for var in item[1]:
            if not hasattr(_this_mod, var):
                raise Exception(
                    "Missing required setting %s. See the "
                    "documentation for this setting at "
                    "expedient.clearinghouse.defaultsettings.%s"
                    % (var, item[0])
                )

except ImportError as e:
    if "No module named localsettings" in "%s" % e:
        print(
            "ERROR: No localsettings module defined. Please run the "
            " 'bootstrap_local_settings' command if you have not yet "
            "created a localsettings module and add the parent "
            "directory to your PYTHONPATH. Proceeding with missing "
            "required settings."
        )
    else:
        raise

# Logging
from expedient.common import loggingconf
import logging

if DEBUG:
    loggingconf.set_up(logging.DEBUG, LOGGING_LEVELS)
else:
    loggingconf.set_up(logging.INFO, LOGGING_LEVELS)


#GENI CONTROL FRAMEWORK SETTINGS (NOT NEEDED AT THIS MOMENT)
GCF_BASE_NAME = "expedient//your_affiliation"
GCF_URN_PREFIX = "expedient:your_afiliation"

#OFREG URL
OFREG_URL = " https://register.fp7-ofelia.eu"
OFREG_RESET_PATH = '/password_reset/forgotten'


OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+expedient:your_affiliation:openflow"
OPENFLOW_GAPI_AM_URN = OPENFLOW_GAPI_RSC_URN_PREFIX+"+am"

#Openflow Test (NOT NEEDED, BUT KEPT HERE JUST IN CASE)
MININET_VMS = [
    ("84.88.41.12", 22),
]

#Monitoring
MONITORING_INTERVAL = 38

