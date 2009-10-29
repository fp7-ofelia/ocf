### $Id$
### $URL$

from sfa.trust.credential import *
from sfa.trust.rights import *
from sfa.util.faults import *
from sfa.util.method import Method
from sfa.util.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.trust.gid import GID
from sfa.util.record import GeniRecord
from sfa.util.genitable import *
from sfa.util.debug import log

class get_credential(Method):
    """
    Retrive a credential for an object
    If cred == Nonee then the behavior reverts to get_self_credential

    @param cred credential object specifying rights of the caller
    @param type type of object (user | slice | sa | ma | node)
    @param hrn human readable name of object

    @return the string representation of a credential object  
    """

    interfaces = ['registry']
    
    accepts = [
        Mixed(Parameter(str, "credential"),
              Parameter(None, "No credential")),  
        Parameter(str, "Human readable name (hrn)"),
        Parameter(str, "Request hash")
        ]

    returns = Parameter(str, "String representation of a credential object")

    def call(self, cred, type, hrn, request_hash):
        if not cred:
            return self.get_self_credential(type, hrn, request_hash)

        # authenticate the cred
        self.api.auth.authenticateCred(cred, [cred, type, hrn], request_hash)
        self.api.auth.check(cred, 'getcredential')
        self.api.auth.verify_object_belongs_to_me(hrn)
        auth_hrn = self.api.auth.get_authority(hrn)

        # Is this a root or sub authority 
        if not auth_hrn or hrn == self.api.config.SFA_INTERFACE_HRN:
            auth_hrn = hrn
        auth_info = self.api.auth.get_auth_info(auth_hrn)
        table = GeniTable()
        records = table.find({'type': type, 'hrn': hrn})
        if not records:
            raise RecordNotFound(hrn)
        record = records[0]
        # verify_cancreate_credential requires that the member lists
        # (researchers, pis, etc) be filled in
        self.api.fill_record_info(record)

        rights = self.api.auth.determine_user_rights(self.api.auth.client_cred, record)
        if rights.is_empty():
            raise PermissionError(self.api.auth.client_cred.get_gid_object().get_hrn() + " has no rights to " + record.get_name())

        # TODO: Check permission that self.client_cred can access the object

        gid = record['gid']
        gid_object = GID(string=gid)

        new_cred = Credential(subject = gid_object.get_subject())
        new_cred.set_gid_caller(self.api.auth.client_gid)
        new_cred.set_gid_object(gid_object)
        new_cred.set_issuer(key=auth_info.get_pkey_object(), subject=auth_hrn)
        new_cred.set_pubkey(gid_object.get_pubkey())
        new_cred.set_privileges(rights)
        new_cred.set_delegate(True)

        auth_kind = "authority,ma,sa"
        new_cred.set_parent(self.api.auth.hierarchy.get_auth_cred(auth_hrn, kind=auth_kind))

        new_cred.encode()
        new_cred.sign()

        return new_cred.save_to_string(save_parents=True)

    def get_self_credential(self, type, hrn, request_hash):
        """
        get_self_credential a degenerate version of get_credential used by a client
        to get his initial credential when de doesnt have one. This is the same as
        get_credetial(..., cred = None, ...)

        The registry ensures that the client is the principal that is named by
        (type, name) by comparing the public key in the record's  GID to the
        private key used to encrypt the client side of the HTTPS connection. Thus
        it is impossible for one principal to retrive another principal's
        credential without having the appropriate private key.

        @param type type of object (user | slice | sa | ma | node)
        @param hrn human readable name of authority to list
        @return string representation of a credential object
        """
        self.api.auth.verify_object_belongs_to_me(hrn)
        auth_hrn = self.api.auth.get_authority(hrn)
         
        # if this is a root or sub authority get_authority will return
        # an empty string
        if not auth_hrn or hrn == self.api.config.SFA_INTERFACE_HRN:
            auth_hrn = hrn

        auth_info = self.api.auth.get_auth_info(auth_hrn)

        # find a record that matches
        record = None
        table = GeniTable()
        records = table.findObjects({'type': type, 'hrn':  hrn})
        if not records:
            raise RecordNotFound(hrn)
        record = records[0]
        gid = record.get_gid_object()
        rights = self.api.auth.determine_user_rights(None, record)
        if rights.is_empty():
            raise PermissionError(gid.get_hrn() + " has no rights to " + record.get_name())
       
        # authenticate the gid
        gid_str = gid.save_to_string(save_parents=True)
        self.api.auth.authenticateGid(gid_str, [None, type, hrn], request_hash)

        # create the credential
        gid = record.get_gid_object()
        cred = Credential(subject = gid.get_subject())
        cred.set_gid_caller(gid)
        cred.set_gid_object(gid)
        cred.set_issuer(key=auth_info.get_pkey_object(), subject=auth_hrn)
        cred.set_pubkey(gid.get_pubkey())
        cred.set_privileges(rights)
        cred.set_delegate(True)

        auth_kind = "authority,sa,ma"
        cred.set_parent(self.api.auth.hierarchy.get_auth_cred(auth_hrn, kind=auth_kind))

        cred.encode()
        cred.sign()
        return cred.save_to_string(save_parents=True)
