from foam.sfa.util.faults import RecordNotFound
from foam.sfa.util.method import Method

from foam.sfa.trust.credential import Credential

from foam.sfa.util.parameter import Parameter, Mixed

class GetGids(Method):
    """
    Get a list of record information (hrn, gid and type) for 
    the specified hrns.

    @param cred credential string 
    @param cert certificate string 
    @return    
    """

    interfaces = ['registry']
    
    accepts = [
        Mixed(Parameter(str, "Human readable name (hrn or xrn)"), 
              Parameter(type([str]), "List of Human readable names (hrn or xrn)")),
        Mixed(Parameter(str, "Credential string"),
              Parameter(type([str]), "List of credentials")), 
        ]

    returns = [Parameter(dict, "Dictionary of gids keyed on hrn")]
    
    def call(self, xrns, creds):
        # validate the credential
        valid_creds = self.api.auth.checkCredentials(creds, 'getgids')
        # xxxpylintxxx origin_hrn is unused..
        origin_hrn = Credential(string=valid_creds[0]).get_gid_caller().get_hrn()
        
        # resolve the record
        records = self.api.manager.Resolve(self.api, xrns, details = False)
        if not records:
            raise RecordNotFound(xrns)

        allowed_fields =  ['hrn', 'type', 'gid']
        for record in records:
            for key in record.keys():
                if key not in allowed_fields:
                    del(record[key])
        return records    
