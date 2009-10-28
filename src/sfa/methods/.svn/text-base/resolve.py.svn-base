### $Id$
### $URL$
import traceback
from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.util.record import GeniRecord
from sfa.util.genitable import GeniTable
from sfa.util.debug import log
from sfa.server.registry import Registries
from sfa.util.prefixTree import prefixTree
from sfa.trust.credential import Credential

class resolve(Method):
    """
    Resolve a record.

    @param cred credential string authorizing the caller
    @param hrn human readable name to resolve
    @return a list of record dictionaries or empty list     
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
        self.api.auth.check(cred, 'resolve')
        if caller_cred==None:
            caller_cred=cred

        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), hrn, self.name))
        good_records = [] 

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
                records = registries[registry_hrn].resolve(credential, hrn, caller_cred=caller_cred)
                good_records = [record.as_dict() for record in records]
                if good_records:
                    return good_records
            except:
                traceback.print_exc()

        # if we still havnt found the record yet, try the local registry
        table = GeniTable()
        records = table.findObjects(hrn)
        if not records:
            raise RecordNotFound(hrn) 
        for record in records:
            try:
                self.api.fill_record_info(record)
                good_records.append(dict(record))
            except PlanetLabRecordDoesNotExist:
                # silently drop the ones that are missing in PL
                print >> log, "ignoring geni record ", record['hrn'], \
                              " because pl record does not exist"
                table.remove(record)


        return good_records    
            
