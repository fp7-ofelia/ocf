### $Id: policy.py 14422 2009-07-09 18:23:51Z thierry $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/util/policy.py $

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
 
