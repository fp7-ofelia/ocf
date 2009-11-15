from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.util.record import GeniRecord
from sfa.util.genitable import GeniTable
from sfa.util.debug import log
from sfa.trust.credential import Credential
from sfa.util.misc import *
from types import StringTypes

class remove_remote_object(Method):
    """
    Remove an object from the PLC records of a federated aggregate. 
    This method will be called by registry.remove() while removing 
    a record from the local aggreage's PLCDB and sfa table. This 
    method need not be directly called by end-user.
    
    @param cred credential string
    @param hrn human readbale name of record to be removed
    @param record record as stored in the authoritative registry

    @return 1 if successful, faults otherwise 
    """

    interfaces = ['registry']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name (hrn) of record to be removed"),
        Parameter(dict, "Record dictionary as stored in the authoritative registry")
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, cred, hrn, record, caller_cred=None):
        self.api.auth.check(cred, "remove")
	if caller_cred==None:
	   caller_cred=cred
	
	#log the call
	self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, Credential(string=caller_cred).get_gid_caller().get_hrn(), hrn, self.name))
        self.api.auth.verify_object_permission(hrn)
        type = record['type']
	peer=self.get_peer(hrn)
	if peer:
           if type == "user":
               peer_records = self.api.plshell.GetPersons(self.api.plauth, {'peer_person_id' : record['pointer']})
               if not peer_records:
                  return 1
               peer_record=peer_records[0]
               self.api.plshell.UnBindObjectFromPeer(self.api.plauth, 'person', peer_record['person_id'], peer)
               self.api.plshell.DeletePerson(self.api.plauth, peer_record['person_id'])
           elif type == "slice":
               peer_records=self.api.plshell.GetSlices(self.api.plauth, {'peer_slice_id' : record['pointer']})
	       if not peer_records:
                  return 1
	       peer_record=peer_records[0]
	       self.api.plshell.UnBindObjectFromPeer(self.api.plauth, 'slice', peer_record['slice_id'], peer)
               self.api.plshell.DeleteSlice(self.api.plauth, peer_record['slice_id'])
           elif type == "authority":
               peer_records=self.api.plshell.GetSites(self.api.plauth, {'peer_site_id' : record['pointer']})
               if not peer_records:
                  return 1
               peer_record=peer_records[0]
               self.api.plshell.UnBindObjectFromPeer(self.api.plauth, 'site', peer_record['site_id'], peer)
               self.api.plshell.DeleteSite(self.api.plauth, peer_record['site_id'])
           else:
               raise UnknownGeniType(type)

           return 1

	else:
	  # Remove objects from remote agg. where no RefreshPeer Federation exists
	  # yet to figure out the mechanism to identify the correct object in the PLCDB
          # on the remote aggregate
	     pass

    def get_peer(self, hrn):
	# Becaues of myplc federation,  we first need to determine if this
        # slice belongs to out local plc or a myplc peer. We will assume it
        # is a local site, unless we find out otherwise
        peer = None
        # get this slice's authority (site)
        slice_authority = get_authority(hrn)

        # get this site's authority (sfa root authority or sub authority)
        site_authority = get_authority(slice_authority).lower()
	if not site_authority:
           site_authority = slice_authority		

        # check if we are already peered with this site_authority, if so
        peers = self.api.plshell.GetPeers(self.api.plauth, {}, ['peer_id', 'peername', 'shortname', 'hrn_root'])
        for peer_record in peers:
            names = [name.lower() for name in peer_record.values() if isinstance(name, StringTypes)]
            if site_authority in names:
                peer = peer_record['shortname']

        return peer


