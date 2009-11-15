### $Id: get_slices.py 14387 2009-07-08 18:19:11Z faiyaza $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/methods/get_slices.py $

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
