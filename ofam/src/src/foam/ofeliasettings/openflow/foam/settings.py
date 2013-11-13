#Vasileios: to be heavily edited

'''Pull all the default settings and then all overrides.
Created on Sep 2, 2010

@author: Peyman Kazemian
'''
import sys, traceback

from openflow.optin_manager.defaultsettings.django import *
from openflow.optin_manager.defaultsettings.database import *
from openflow.optin_manager.defaultsettings.admins import *
from openflow.optin_manager.defaultsettings.email import *
from openflow.optin_manager.defaultsettings.optin_manager import *
from openflow.optin_manager.defaultsettings.site import *
from openflow.optin_manager.defaultsettings.openflowtests import *
from openflow.optin_manager.defaultsettings.tests import *
from openflow.optin_manager.defaultsettings.admin_manager import *

# Import the list of required variables
from openflow.optin_manager.defaultsettings.required import REQUIRED_SETTINGS

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
                    "openflow.optin_manager.defaultsettings.%s"
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

#
# For testing. Not really needed, since the line is commented in
# REQUIRED_SETTINGS.
#
MININET_VMS = [
    ("84.88.41.12", 22),
]

# Default monitoring interval in seconds.
#
MONITORING_INTERVAL = 38
