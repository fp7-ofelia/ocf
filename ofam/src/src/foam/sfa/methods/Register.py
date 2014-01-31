from foam.sfa.util.method import Method

from foam.sfa.trust.credential import Credential

from foam.sfa.util.parameter import Parameter, Mixed

class Register(Method):
    """
    Register an object with the registry. In addition to being stored in the
    SFA database, the appropriate records will also be created in the
    PLC databases
    
    @param cred credential string
    @param record_dict dictionary containing record fields
    
    @return gid string representation
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(dict, "Record dictionary containing record fields"),
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")),
        ]

    returns = Parameter(int, "String representation of gid object")
    
    def call(self, record, creds):
        # validate cred    
        valid_creds = self.api.auth.checkCredentials(creds, 'register')
        
        # verify permissions
        hrn = record.get('hrn', '')
        self.api.auth.verify_object_permission(hrn)

        #log the call
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, origin_hrn, hrn, self.name))
        
        return self.api.manager.Register(self.api, record)
