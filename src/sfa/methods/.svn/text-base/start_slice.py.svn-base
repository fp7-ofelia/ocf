### $Id$
### $URL$

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.plc.slices import Slices

class start_slice(Method):
    """
    Start the specified slice      

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name of slice to instantiate
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to instantiate"),
        Parameter(str, "Request hash")
        ]

    returns = [Parameter(int, "1 if successful")]
    
    def call(self, cred, hrn, request_hash):
        # This cred will be an slice cred, not a user, so we cant use it to
        # authenticate the caller's request_hash. Let just get the caller's gid
        # from the cred and authenticate using that
        client_gid = Credential(string=cred).get_gid_caller()
        client_gid_str = client_gid.save_to_string(save_parents=True)
        self.api.auth.authenticateGid(client_gid_str, [cred, hrn], request_hash)
        self.api.auth.check(cred, 'startslice')
        slices = Slices(self.api)
        slices.start_slice(hrn)
        
        return 1 
