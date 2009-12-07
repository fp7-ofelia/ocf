### $Id$
### $URL$

import os
import sys
import datetime
import time

from sfa.util.geniserver import *
from sfa.util.geniclient import *
from sfa.util.faults import *
from sfa.util.misc import *

class SliceMgr(GeniServer):

  
    ##
    # Create a new slice manager object.
    #
    # @param ip the ip address to listen on
    # @param port the port to listen on
    # @param key_file private key filename of registry
    # @param cert_file certificate filename containing public key (could be a GID file)     

    def __init__(self, ip, port, key_file, cert_file, config = "/etc/sfa/sfa_config"):
        GeniServer.__init__(self, ip, port, key_file, cert_file)
        self.server.interface = 'slicemgr'      
