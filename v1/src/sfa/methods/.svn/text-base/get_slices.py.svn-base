### $Id$
### $URL$

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.plc.slices import Slices

class get_slices(Method):
    """
    Get a list of instantiated slices at this authority.      

    @param cred credential string specifying the rights of the caller
    @return list of human readable slice names (hrn).  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        ]

    returns = [Parameter(str, "Human readable slice name (hrn)")]
    
    def call(self, cred):
       
        self.api.auth.check(cred, 'listslices')
        slices = Slices(self.api)
        slices.refresh()    
        return slices['hrn']
