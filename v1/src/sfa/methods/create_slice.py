### $Id: create_slice.py 15253 2009-10-08 16:13:49Z anil $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/methods/create_slice.py $

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.plc.slices import Slices
from sfa.util.config import Config
# RSpecManager_pl is not used. It's used to make sure the module is in place.
import sfa.rspecs.aggregates.rspec_manager_pl
from sfa.trust.credential import Credential
from sfatables.runtime import SFATablesRules


class create_slice(Method):
    """
    Instantiate the specified slice according to whats defined in the specified rspec      

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name of slice to instantiate
    @param rspec resource specification
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to instantiate"),
        Parameter(str, "Resource specification"),
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, cred, hrn, requested_rspec, caller_cred=None):
        if caller_cred==None:
            caller_cred=cred
        
        self.api.auth.check(cred, 'createslice')

        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), hrn, self.name))

        sfa_aggregate_type = Config().get_aggregate_rspec_type()
        rspec_manager = __import__("sfa.rspecs.aggregates.rspec_manager_"+sfa_aggregate_type, fromlist = ["sfa.rspecs.aggregates"])
        #Filter the incoming rspec using sfatables
        incoming_rules = SFATablesRules('OUTGOING')
            
        #incoming_rules.set_slice(hrn) # This is a temporary kludge. Eventually, we'd like to fetch the context requested by the match/target

        contexts = incoming_rules.contexts
        request_context = rspec_manager.fetch_context(hrn, Credential(string=caller_cred).get_gid_caller().get_hrn(), contexts)
        incoming_rules.set_context(request_context)
        rspec = incoming_rules.apply(requested_rspec)

        if (sfa_aggregate_type == 'pl'):
            slices = Slices(self.api, caller_cred=caller_cred)
            slices.create_slice(hrn, rspec)    
        else:
            # To clean up after July 21 - SB    
            rspec = rspec_manager.create_slice(self.api, hrn, rspec)

        
        return 1 
