'''Contains management utilities
Created on Aug 25, 2010

@author: jnaous
'''
import pkg_resources
import os
from expedient.clearinghouse.defaultsettings.django import CONF_DIR
from expedient.clearinghouse.defaultsettings.required import REQUIRED_SETTINGS

def bootstrap_local_settings(conf_dir=CONF_DIR):
    """
    Create a localsettings module in C{conf_dir}.
    
    @keyword conf_dir: location of the localsettings.py file. Defaults
        to CONF_DIR.
    """
    loc = os.path.join(conf_dir, "localsettings.py")
    pkg_resources.ensure_directory(loc)
    if os.access(loc, os.F_OK):
        print "ERROR: Found localsettings already. "\
            "Cowardly refusing to overwrite."
        return
    print "Creating skeleton localsettings.py file. in %s" % conf_dir
    f = open(loc, mode="w")
    # write the conf dir location
    f.write("CONF_DIR = '%s'\n" % conf_dir)
    for item in REQUIRED_SETTINGS:
        for var in item[1]:
            f.write("%s = None\n" % var)
    f.close()
    print "Done."
