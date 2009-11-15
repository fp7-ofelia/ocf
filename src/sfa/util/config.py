##
# Geniwrapper Configuration Info
#
# This module holds configuration parameters for geniwrapper. There are two
# main pieces of information that are used: the database connection and
# the PLCAPI connection
##

##
# Geniwrapper uses a MYSQL database to store records. This database may be
# co-located with the PLC database, or it may be a separate database. The
# following parameters define the connection to the database.
#
# Note that Geniwrapper does not access any of the PLC databases directly via
# a mysql connection; All PLC databases are accessed via PLCAPI.

### $Id: config.py 15186 2009-09-30 23:20:21Z bakers $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/util/config.py $

import os.path
import traceback

from sfa.util.debug import log

class Config:
    """
    Parse the bash/Python/PHP version of the configuration file. Very
    fast but no type conversions.
    """

    def __init__(self, config_file = "/etc/sfa/sfa_config"):
        self.config_file = None
        self.config_path = None
        self.load(config_file)

    def load(self, config_file):
        try:
            execfile(config_file, self.__dict__)
            self.config_file = config_file
            self.config_path = os.path.dirname(config_file)
        except IOError, e:
            raise IOError, "Could not find the configuration file: %s" % config_file

    def get_trustedroots_dir(self):
        return self.config_path + os.sep + 'trusted_roots'

    def get_openflow_aggrMgr_info(self):
        aggr_mgr_ip = 'localhost'
        if (hasattr(self,'OPENFLOW_AGGREGATE_MANAGER_IP')):
            aggr_mgr_ip = self.OPENFLOW_AGGREGATE_MANAGER_IP

        aggr_mgr_port = 2603
        if (hasattr(self,'OPENFLOW_AGGREGATE_MANAGER_PORT')):
            aggr_mgr_port = self.OPENFLOW_AGGREGATE_MANAGER_PORT

        return (aggr_mgr_ip,aggr_mgr_port)

    def get_aggregate_rspec_type(self):
        if (hasattr(self,'SFA_AGGREGATE_RSPEC_TYPE')):
            return self.SFA_AGGREGATE_RSPEC_TYPE
        else:
            return "pl"

    def get_plc_dbinfo(self):
        return {
            'dbname' : self.SFA_PLC_DB_NAME,
            'address' : self.SFA_PLC_DB_HOST,
            'port' : self.SFA_PLC_DB_PORT,
            'user' : self.SFA_PLC_DB_USER,
            'password' : self.SFA_PLC_DB_PASSWORD
            }

    ##
    # Geniwrapper uses a PLCAPI connection to perform operations on the registry,
    # such as creating and deleting slices. This connection requires an account
    # on the PLC server with full administrator access.
    #
    # The Url parameter controls whether the connection uses PLCAPI directly (i.e.
    # Geniwrapper is located on the same machine as PLC), or uses a XMLRPC connection
    # to the PLC machine. If you wish to use the API directly, then remove the Url
    # field from the dictionary. 

    def get_plc_auth(self):
        return {
            'AuthMethod': 'capability',
            'Username': self.SFA_PLC_USER,
            'AuthString':  self.SFA_PLC_PASSWORD,
            "Url": self.SFA_PLC_URL
            }
