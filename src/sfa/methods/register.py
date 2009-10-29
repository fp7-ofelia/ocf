### $Id: register.py 15335 2009-10-16 01:58:37Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/methods/register.py $

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

class register(Method):
    """
    Register an object with the registry. In addition to being stored in the
    Geni database, the appropriate records will also be created in the
    PLC databases
    
    @param cred credential string
    @param record_dict dictionary containing record fields
    
    @return gid string representation
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(dict, "Record dictionary containing record fields"),
        Parameter(str, "Request hash")
        ]

    returns = Parameter(int, "String representation of gid object")
    
    def call(self, cred, record_dict, request_hash, caller_cred=None):
        # This cred will be an authority cred, not a user, so we cant use it to 
        # authenticate the caller's request_hash. Let just get the caller's gid
        # from the cred and authenticate using that 
        client_gid = Credential(string=cred).get_gid_caller()
        client_gid_str = client_gid.save_to_string(save_parents=True)
        self.api.auth.authenticateGid(client_gid_str, [cred], request_hash)
        self.api.auth.check(cred, "register")
        if caller_cred==None:
	        caller_cred=cred
	
        #log the call
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), None, self.name))
        record = GeniRecord(dict = record_dict)
        record['authority'] = get_authority(record['hrn'])
        type = record['type']
        hrn = record['hrn']
        self.api.auth.verify_object_permission(hrn)
        auth_info = self.api.auth.get_auth_info(record['authority'])
        pub_key = None  
        # make sure record has a gid
        if 'gid' not in record:
            uuid = create_uuid()
            pkey = Keypair(create=True)
            if 'key' in record and record['key']:
                if isinstance(record['key'], list):
                    pub_key = record['key'][0]
                else:
                    pub_key = record['key']
                pkey = convert_public_key(pub_key)
            
            gid_object = self.api.auth.hierarchy.create_gid(hrn, uuid, pkey)
            gid = gid_object.save_to_string(save_parents=True)
            record['gid'] = gid
            record.set_gid(gid)

        # check if record already exists
        table = GeniTable()
        existing_records = table.find({'type': type, 'hrn': hrn})
        if existing_records:
            raise ExistingRecord(hrn)
        else:
            # We will update the pointer later
            record['pointer'] = -1 
            record.set_pointer(-1)
            record_id = table.insert(record)
            record['record_id'] = record_id
 
        if type in ["authority"]:
            # update the tree
            if not self.api.auth.hierarchy.auth_exists(hrn):
                self.api.auth.hierarchy.create_auth(hrn)

            # authorities are special since they are managed by the registry
            # rather than by the caller. We create our own GID for the
            # authority rather than relying on the caller to supply one.

            # get the GID from the newly created authority
            gid = auth_info.get_gid_object()
            record.set_gid(gid.save_to_string(save_parents=True))

            pl_record = self.api.geni_fields_to_pl_fields(type, hrn, record)
            sites = self.api.plshell.GetSites(self.api.plauth, [pl_record['login_base']])
            if not sites:    
                pointer = self.api.plshell.AddSite(self.api.plauth, pl_record)
            else:
                pointer = sites[0]['site_id']

            record.set_pointer(pointer)

        elif (type == "slice"):
            pl_record = self.api.geni_fields_to_pl_fields(type, hrn, record)
            slices = self.api.plshell.GetSlices(self.api.plauth, [pl_record['name']])
            if not slices: 
                pointer = self.api.plshell.AddSlice(self.api.plauth, pl_record)
            else:
                pointer = slices[0]['slice_id']
            record.set_pointer(pointer)

        elif  (type == "user"):
            persons = self.api.plshell.GetPersons(self.api.plauth, [record['email']])
            if not persons:
                pointer = self.api.plshell.AddPerson(self.api.plauth, dict(record))
            else:
                pointer = persons[0]['person_id']
 
            if 'enabled' in record and record['enabled']:
                self.api.plshell.UpdatePerson(self.api.plauth, pointer, {'enabled': record['enabled']})
            # add this persons to the site only if he is being added for the first
            # time by sfa and doesont already exist in plc     
            if not persons or not persons[0]['site_ids']:
                login_base = get_leaf(record['authority'])
                self.api.plshell.AddPersonToSite(self.api.plauth, pointer, login_base)
        
            # What roles should this user have?
            self.api.plshell.AddRoleToPerson(self.api.plauth, 'user', pointer) 
            record.set_pointer(pointer)
            # Add the user's key
            if pub_key:
                self.api.plshell.AddPersonKey(self.api.plauth, pointer, {'key_type' : 'ssh', 'key' : pub_key})

        elif (type == "node"):
            pl_record = self.api.geni_fields_to_pl_fields(type, hrn, record)
            login_base = hrn_to_pl_login_base(record['authority'])
            nodes = self.api.plshell.GetNodes(self.api.plauth, [pl_record['hostname']])
            if not nodes:
                pointer = self.api.plshell.AddNode(self.api.plauth, login_base, pl_record)
            else:
                pointer = nodes[0]['node_id']
            record.set_pointer(pointer)

        else:
            raise UnknownGeniType(type)

        table.update(record)

        # update membership for researchers, pis, owners, operators
        self.api.update_membership(None, record)

        return record.get_gid_object().save_to_string(save_parents=True)
