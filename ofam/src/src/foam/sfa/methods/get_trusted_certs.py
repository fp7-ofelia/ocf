from foam.sfa.util.method import Method

from foam.sfa.trust.auth import Auth
from foam.sfa.trust.credential import Credential

from foam.sfa.util.parameter import Parameter, Mixed

class get_trusted_certs(Method):
    """
    @param cred credential string specifying the rights of the caller
    @return list of gid strings  
    """

    interfaces = ['registry', 'aggregate', 'slicemgr']
    
    accepts = [
        Mixed(Parameter(str, "Credential string"),
              Parameter(None, "Credential not specified"))
        ]

    returns = Parameter(type([str]), "List of GID strings")
    
    def call(self, cred = None):
        # If cred is not specified just return the gid for this interface.
        # This is true when when a peer is attempting to initiate federation
        # with this interface 
        self.api.logger.debug("get_trusted_certs: %r"%cred)
        if not cred:
            gid_strings = []
            for gid in self.api.auth.trusted_cert_list:
                if gid.get_hrn() == self.api.config.SFA_INTERFACE_HRN:
                    gid_strings.append(gid.save_to_string(save_parents=True))   
            return gid_strings

        # authenticate the cred
        self.api.auth.check(cred, 'gettrustedcerts')
        gid_strings = [gid.save_to_string(save_parents=True) for \
                                gid in self.api.auth.trusted_cert_list] 
        
        return gid_strings 
