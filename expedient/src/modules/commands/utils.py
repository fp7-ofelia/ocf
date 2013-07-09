'''Contains management utilities
Created on Aug 25, 2010

@author: jnaous
'''
import os
import pkg_resources
import sys
import MySQLdb
from optparse import OptionParser

from expedient.clearinghouse.defaultsettings.django import CONF_DIR
from expedient.clearinghouse.defaultsettings.required import REQUIRED_SETTINGS

def bootstrap_local_settings(conf_dir=CONF_DIR):
    """
    Create a localsettings module in C{conf_dir}.
    
    @keyword conf_dir: location of the localsettings.py file. Defaults
        to CONF_DIR.
    """
    conf_dir = os.path.abspath(conf_dir)
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

def create_user(root_username, root_password, username, password, db_name, host):
    """Create a database user and give her privileges to create/delete
    databases C{<db_name>} and test_C{<db_name>}."""
    
    try:
        conn = MySQLdb.connect(
            host=host,
            user=root_username,
            passwd=root_password,
        )
        
    except MySQLdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE DATABASE %s;
        GRANT ALL on %s.* TO '%s'@'%s' IDENTIFIED BY '%s';
        GRANT ALL on test_%s.* TO '%s'@'%s';
        """ % (db_name, db_name, username, host, password,
               db_name, username, host)
    )
    cursor.close()
    
def bootstrap_expedient_mysql():
    parser = OptionParser()
    parser.add_option(
        "--confdir",
        action="store", type="string", dest="confdir",
        default="/etc/expedient",
        help="Location of the localsettings file. [default: %default]",
    )
    parser.add_option(
        "--root",
        action="store", type="string", dest="root_username",
        default="root",
        help="root username or the username to use for creating the new user."
            " [default: %default]",
    )
    parser.add_option(
        "--rootpassword",
        action="store", type="string", dest="root_password",
        default="",
        help="root password."
            " [default: '']",
    )
    options, _ = parser.parse_args()
    
    sys.path.append(options.confdir)
    
    import expedient.clearinghouse.settings as settings
    
    create_user(
        options.root_username,
        options.root_password or "",
        settings.DATABASE_USER,
        settings.DATABASE_PASSWORD,
        settings.DATABASE_NAME,
        settings.DATABASE_HOST or "localhost",
    )
