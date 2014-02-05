from foam.sfa.util.xrn import Xrn
from foam.sfa.util.method import Method

from foam.sfa.trust.credential import Credential

from foam.sfa.util.parameter import Parameter, Mixed

class Remove(Method):
    """
    Remove an object from the registry. If the object represents a PLC object,
    then the PLC records will also be removed.
    
    @param cred credential string
    @param type record type
    @param xrn human readable name of record to remove (hrn or urn)

    @return 1 if successful, faults otherwise 
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Human readable name of slice to instantiate (hrn or urn)"),
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")),
        Mixed(Parameter(str, "Record type"),
              Parameter(None, "Type not specified")),
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, xrn, creds, type):
        xrn=Xrn(xrn,type=type)
        
        # validate the cred
        valid_creds = self.api.auth.checkCredentials(creds, "remove")
        self.api.auth.verify_object_permission(xrn.get_hrn())

        #log the call
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()
        self.api.logger.info("interface: %s\tmethod-name: %s\tcaller-hrn: %s\ttarget-urn: %s"%(
                self.api.interface, self.name, origin_hrn, xrn.get_urn()))

        return self.api.manager.Remove(self.api, xrn) 
