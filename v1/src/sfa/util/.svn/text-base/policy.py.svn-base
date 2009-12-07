### $Id$
### $URL$

import os

from sfa.util.storage import *
from sfa.util.debug import log

class Policy(SimpleStorage):

    def __init__(self, api):
        self.api = api
        path = self.api.config.SFA_BASE_DIR
        filename = ".".join([self.api.interface, self.api.hrn, "policy"])    
        filepath = path + os.sep + filename
        self.policy_file = filepath
        default_policy = {'slice_whitelist': [],
                          'slice_blacklist': [],
                          'node_whitelist': [],
                          'node_blacklist': []} 
        SimpleStorage.__init__(self, self.policy_file, default_policy)
        self.load()          
 
