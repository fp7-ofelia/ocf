### $Id: create_gid.py 14420 2009-07-09 17:18:07Z thierry $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/methods/create_gid.py $

from sfa.trust.certificate import Keypair 

from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed

from sfa.trust.gid import create_uuid
from sfa.trust.auth import Auth

class create_gid(Method):
    """
    Create a new GID. For MAs and SAs that are physically located on the
    registry, this allows a owner/operator/PI to create a new GID and have it
    signed by his respective authority.
    
    @param cred credential of caller
    @param name hrn for new GID
    @param uuid unique identifier for new GID
    @param pkey_string public-key string (TODO: why is this a string and not a keypair object?)
    
    @return the string representation of a GID object
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name (hrn)"),
        Mixed(Parameter(str, "Unique identifier for new GID (uuid)"),
              Parameter(None, "Unique identifier (uuid) not specified")),   
        Parameter(str, "public-key string")
        ]

    returns = Parameter(str, "String represeneation of a GID object")
    
    def call(self, cred, hrn, uuid, pubkey_str):
        self.api.auth.check(cred, "getcredential")
        self.api.auth.verify_object_belongs_to_me(hrn)
        self.api.auth.verify_object_permission(hrn)

        if uuid == None:
            uuid = create_uuid()

        pkey = Keypair()
        pkey.load_pubkey_from_string(pubkey_str)
        gid = self.api.auth.hierarchy.create_gid(hrn, uuid, pkey)

        return gid.save_to_string(save_parents=True)
