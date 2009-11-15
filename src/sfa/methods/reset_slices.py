### $Id: reset_slices.py 14387 2009-07-08 18:19:11Z faiyaza $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/methods/reset_slices.py $

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.plc.slices import Slices

class reset_slices(Method):
    """
    Reset the specified slice      

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name of slice to instantiate
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to instantiate"),
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, cred, hrn):
       
        self.api.auth.check(cred, 'resetslice')
        ## XX Not yet implemented
 
        return 1 
