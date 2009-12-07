### $Id$
### $URL$

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.trust.credential import Credential

from sfa.plc.slices import Slices

class delete_slice(Method):
    """
    Remove the slice from all nodes.      

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name specifying the slice to delete
    @return 1 if successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to delete"),
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, cred, hrn, caller_cred=None):
       
	if caller_cred==None:
	   caller_cred=cred
	#log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), hrn, self.name))

        self.api.auth.check(cred, 'deleteslice')
        slices = Slices(self.api, caller_cred=caller_cred)
        slices.delete_slice(hrn)
        return 1
