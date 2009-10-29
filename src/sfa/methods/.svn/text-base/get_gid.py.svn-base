# * require certificate as an argument
# * lookup gid in db
# * get pubkey from gid
# * if certifacate matches pubkey from gid, return gid, else raise exception
#  if not peer.is_pubkey(gid.get_pubkey()):
#            raise ConnectionKeyGIDMismatch(gid.get_subject())

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.trust.gid import GID
from sfa.trust.certificate import Certificate
from sfa.util.genitable import GeniTable

class get_gid(Method):
    """
    Returns the client's gid if one exists      

    @param cert certificate string 
    @return client gid  
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Certificate string"),
        Parameter(str, "Human readable name (hrn)"),  
        Parameter(str, "Request hash")  
        ]

    returns = [Parameter(dict, "Aggregate interface information")]
    
    def call(self, cert, hrn, type, requestHash):
      
        self.api.auth.verify_object_belongs_to_me(hrn)
        certificate = Certificate(string=cert) 
        table = GeniTable()
        records = table.find({'hrn': hrn, 'type': type})
        if not records:
            raise RecordNotFound(hrn)
        record = records[0]
        gidStr = record['gid']
        gid = GID(string=gidStr)
         
        if not certificate.is_pubkey(gid.get_pubkey()):
            raise ConnectionKeyGIDMismatch(gid.get_subject())
        
        # authenticate the gid
        self.api.auth.authenticateGid(gidStr, [cert, hrn, type], requestHash)
        
        return gidStr 
