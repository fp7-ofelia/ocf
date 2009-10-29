### $Id: get_resources.py 15336 2009-10-16 03:27:30Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/methods/get_resources.py $

from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.util.config import Config
from sfa.plc.nodes import Nodes
# RSpecManager_pl is not used. This line is a check that ensures that everything is in place for the import to work.
import sfa.rspecs.aggregates.rspec_manager_pl
from sfa.trust.credential import Credential
from sfatables.runtime import SFATablesRules

class get_resources(Method):
    """
    Get an resource specification (rspec). The rspec may describe the resources
    available at an authority or the resources being used by a slice.      

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name of the slice we are interesed in or None 
           for an authority.  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        Mixed(Parameter(str, "Human readable name (hrn)"),
              Parameter(None, "hrn not specified")),
        Parameter(str, "Request hash")
        ]

    returns = Parameter(str, "String representatin of an rspec")
    
    def call(self, cred, hrn=None, request_hash = None, caller_cred=None):
        sfa_aggregate_type = Config().get_aggregate_rspec_type()

        # This cred will be an authority cred, not a user, so we cant use it to 
        # authenticate the caller's request_hash. Let just get the caller's gid
        # from the cred and authenticate using that 
        client_gid = Credential(string=cred).get_gid_caller()
        client_gid_str = client_gid.save_to_string(save_parents=True)
        self.api.auth.authenticateGid(client_gid_str, [cred,hrn], request_hash)
        self.api.auth.check(cred, 'listnodes')
        if caller_cred==None:
            caller_cred=cred

        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), hrn, self.name))

        # This code needs to be cleaned up so that 'pl' is treated as just another RSpec manager.
        # The change ought to be straightforward as soon as we define PL's new RSpec.

        rspec_manager = __import__("sfa.rspecs.aggregates.rspec_manager_"+sfa_aggregate_type,
                                   fromlist = ["sfa.rspecs.aggregates"])
        if (sfa_aggregate_type == 'pl'):
            nodes = Nodes(self.api, caller_cred=caller_cred)
            if hrn:
                rspec = nodes.get_rspec(hrn)
            else:
                nodes.refresh()
                rspec = nodes['rspec']
        else:
            rspec = rspec_manager.get_rspec(self.api, hrn)

        # Filter the outgoing rspec using sfatables
        outgoing_rules = SFATablesRules('OUTGOING')

        request_context = rspec_manager.fetch_context(
            hrn,
            Credential(string=caller_cred).get_gid_caller().get_hrn(),
            outgoing_rules.contexts)
        outgoing_rules.set_context(request_context)
        filtered_rspec = outgoing_rules.apply(rspec)

        return filtered_rspec
