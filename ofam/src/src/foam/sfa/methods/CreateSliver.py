from foam.sfa.util.faults import SfaInvalidArgument, InvalidRSpec
from foam.sfa.util.xrn import urn_to_hrn
from foam.sfa.trust.credential import Credential
from foam.sfa.trust.auth import Auth

class CreateSliver:

    def __init__(self, slice_xrn, creds, users, options, **kwargs):

        hrn, type = urn_to_hrn(slice_xrn)

        # Find the valid credentials
        valid_creds = Auth().checkCredentials(creds, 'createsliver', hrn)
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()

        # make sure users info is specified
        if not users:
            msg = "'users' must be specified and cannot be null. You may need to update your client." 
            raise SfaInvalidArgument(name='users', extra=msg)  

        return 
