from vt_manager.communication.sfa.util.xrn import urn_to_hrn
from vt_manager.communication.sfa.trust.auth import Auth

class SliverStatus:

    def __init__(self, slice_xrn, creds, options, **kwargs):
        hrn, type = urn_to_hrn(slice_xrn)
        valid_creds = Auth().checkCredentials(creds, 'sliverstatus', hrn)
        return
    
