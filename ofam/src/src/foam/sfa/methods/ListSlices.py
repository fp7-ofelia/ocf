from foam.sfa.util.method import Method

from foam.sfa.trust.credential import Credential
 
from foam.sfa.util.parameter import Parameter, Mixed

class ListSlices(Method):
    """
    List the slices instantiated at this interface       

    @param cred credential string specifying the rights of the caller
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr', 'component']
    
    accepts = [
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")),
        Parameter(dict, "options"),
        ]

    returns = Parameter(list, "List of slice names")
    
    def call(self, creds, options):
        valid_creds = self.api.auth.checkCredentials(creds, 'listslices')

        #log the call
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()
        self.api.logger.info("interface: %s\tcaller-hrn: %s\tmethod-name: %s"%(self.api.interface, origin_hrn, self.name))

        return self.api.manager.ListSlices(self.api, creds, options)
 
