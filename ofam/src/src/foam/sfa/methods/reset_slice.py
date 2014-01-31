from foam.sfa.util.xrn import urn_to_hrn
from foam.sfa.util.method import Method

from foam.sfa.util.parameter import Parameter, Mixed

class reset_slice(Method):
    """
    Reset the specified slice      

    @param cred credential string specifying the rights of the caller
    @param xrn human readable name of slice to instantiate (hrn or urn)
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr', 'component']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to instantiate (hrn or urn)"),
        Mixed(Parameter(str, "Human readable name of the original caller"),
              Parameter(None, "Origin hrn not specified"))
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, cred, xrn, origin_hrn=None):
        hrn, type = urn_to_hrn(xrn)
        self.api.auth.check(cred, 'resetslice', hrn)
        self.api.manager.reset_slice (self.api, xrn)
        return 1 
