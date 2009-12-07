### $Id: register.py 15001 2009-09-11 20:18:54Z tmack $
### $URL: https://svn.planet-lab.org/svn/sfa/trunk/sfa/methods/register.py $

from sfa.trust.certificate import Keypair, convert_public_key
from sfa.trust.gid import *

from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.util.record import GeniRecord
from sfa.util.genitable import GeniTable
from sfa.util.debug import log
from sfa.trust.auth import Auth
from sfa.trust.gid import create_uuid
from sfa.trust.credential import Credential

class register_peer_object(Method):
    """
    Register a peer object with the registry. In addition to being stored in the
    Geni database, the appropriate records will also be created in the
    PLC databases
    
    @param cred credential string
    @param record_dict dictionary containing record fields
    
    @return gid string representation
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(dict, "Record dictionary containing record fields")
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, cred, record_dict, caller_cred=None):
        self.api.auth.check(cred, "register")
        if caller_cred==None:
	        caller_cred=cred
        	
        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), None, self.name))

        # make sure this is a peer record
        if 'peer_authority' not in record_dict or \
           not record_dict['peer_authority']: 
            raise GeniInvalidArgument, "peer_authority must be specified" 

        record = GeniRecord(dict = record_dict)
        type, hrn, peer_authority = record['type'], record['hrn'], record['peer_authority']
        record['authority'] = get_authority(record['hrn'])
        # verify permissions
        self.api.auth.verify_cred_is_me(cred)

        # check if record already exists
        table = GeniTable()
        existing_records = table.find({'type': type, 'hrn': hrn, 'peer_authority': peer_authority})
        if existing_records:
            for existing_record in existing_records:
                if existing_record['pointer'] != record['pointer']:
                    record['record_id'] = existing_record['record_id']
                    table.update(record)
            return 1
        record_id = table.insert(record)
 
        return 1
