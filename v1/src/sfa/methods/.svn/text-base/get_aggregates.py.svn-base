### $Id: get_slices.py 14387 2009-07-08 18:19:11Z faiyaza $
### $URL: https://svn.planet-lab.org/svn/sfa/trunk/sfa/methods/get_aggregates.py $
from types import StringTypes
from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.server.aggregate import Aggregates

class get_aggregates(Method):
    """
    Get a list of connection information for all known aggregates.      

    @param cred credential string specifying the rights of the caller
    @param a Human readable name (hrn), or list of hrns or None
    @return list of dictionaries with aggregate information.  
    """

    interfaces = ['registry', 'aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        
        Mixed(Parameter(str, "Human readable name (hrn)"),
              Parameter(None, "hrn not specified"))  
        ]

    returns = [Parameter(dict, "Aggregate interface information")]
    
    def call(self, cred, hrn = None):
       
        self.api.auth.check(cred, 'list')
        aggregates = Aggregates(self.api)
        hrn_list = [] 
        if hrn:
            if isinstance(hrn, StringTypes):
                hrn_list = [hrn]
            elif isinstance(hrn, list):
                hrn_list = hrn
        
        if not hrn_list:
            interfaces = aggregates.interfaces
        else:
            interfaces = [interface for interface in aggregates.interfaces if interface['hrn'] in hrn_list]
      
        return interfaces
