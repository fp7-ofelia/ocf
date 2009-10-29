### $Id$
### $URL$

from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.util.record import GeniRecord
from sfa.util.genitable import GeniTable
from sfa.server.registry import Registries
from sfa.util.prefixTree import prefixTree
from sfa.trust.credential import Credential

class list(Method):
    """
    List the records in an authority. 

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name of authority to list
    @return list of record dictionaries         
    """
    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name (hrn)"),
        Parameter(str, "Request hash")
        ]

    returns = [GeniRecord]
    
    def call(self, cred, hrn, request_hash, caller_cred=None):
        self.api.auth.authenticateCred(cred, [cred, hrn], request_hash)
        self.api.auth.check(cred, 'list')
        if caller_cred==None:
            caller_cred=cred

        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), hrn, self.name))
        records = []

        # load all know registry names into a prefix tree and attempt to find
        # the longest matching prefix  
        registries = Registries(self.api)
        hrns = registries.keys()
        tree = prefixTree()
        tree.load(hrns)
        registry_hrn = tree.best_match(hrn)

        #if there was no match then this record belongs to an unknow registry
        if not registry_hrn:
            raise MissingAuthority(hrn)
        
        # if the best match (longest matching hrn) is not the local registry,
        # forward the request
        if registry_hrn != self.api.hrn:
            credential = self.api.getCredential()
            try:
                record_list = registries[registry_hrn].list(credential, hrn, caller_cred=caller_cred)
                records = [record.as_dict() for record in record_list]
                if records:
                    return records
            except:
                pass

        # if we still havnt found the record yet, try the local registry
        if not self.api.auth.hierarchy.auth_exists(hrn):
            raise MissingAuthority(hrn)
        
        table = GeniTable()
        records = table.find({'authority': hrn})
        
        return records
