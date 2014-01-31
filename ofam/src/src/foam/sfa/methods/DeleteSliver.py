from foam.sfa.util.xrn import urn_to_hrn
from foam.sfa.util.method import Method
from foam.sfa.util.parameter import Parameter, Mixed
from foam.sfa.trust.auth import Auth
from foam.sfa.trust.credential import Credential

class DeleteSliver:
    
    def __init__(self, xrn, creds, options, **kwargs):
        (hrn, type) = urn_to_hrn(xrn)
        valid_creds = Auth().checkCredentials(creds, 'deletesliver', hrn)
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()


        return #self.api.manager.DeleteSliver(self.api, xrn, creds, options)
 
