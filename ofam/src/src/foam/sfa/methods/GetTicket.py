from foam.sfa.util.xrn import urn_to_hrn
from foam.sfa.util.method import Method
from foam.sfa.util.foam.sfa.ablesRuntime import run_foam.sfa.ables

from foam.sfa.trust.credential import Credential

from foam.sfa.util.parameter import Parameter, Mixed

class GetTicket(Method):
    """
    Retrieve a ticket. This operation is currently implemented on PLC
    only (see SFA, engineering decisions); it is not implemented on
    components.
    
    The ticket is filled in with information from the PLC database. This
    information includes resources, and attributes such as user keys and
    initscripts.
    
    @param cred credential string
    @param name name of the slice to retrieve a ticket for (hrn or urn)
    @param rspec resource specification dictionary
    
    @return the string representation of a ticket object
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Human readable name of slice to retrive a ticket for (hrn or urn)"),
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")),
        Parameter(str, "Resource specification (rspec)"),
        Parameter(type([]), "List of user information"),
        Parameter(dict, "Options")  
        ]

    returns = Parameter(str, "String representation of a ticket object")
    
    def call(self, xrn, creds, rspec, users, options):
        hrn, type = urn_to_hrn(xrn)
        # Find the valid credentials
        valid_creds = self.api.auth.checkCredentials(creds, 'getticket', hrn)
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn() 

        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, origin_hrn, hrn, self.name))

        # filter rspec through foam.sfa.ables
        if self.api.interface in ['aggregate']:
            chain_name = 'OUTGOING'
        elif self.api.interface in ['slicemgr']:
            chain_name = 'FORWARD-OUTGOING'
        rspec = run_foam.sfa.ables(chain_name, hrn, origin_hrn, rspec)
        
        # remove nodes that are not available at this interface from the rspec
        return self.api.manager.GetTicket(self.api, xrn, creds, rspec, users, options)
        
