#
# GeniAPI authentication 
#
### $Id: auth.py 15190 2009-10-01 06:34:06Z bakers $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/trust/auth.py $
#

import time

from sfa.trust.credential import Credential
from sfa.trust.trustedroot import TrustedRootList
from sfa.trust.rights import RightList
from sfa.util.faults import *
from sfa.trust.hierarchy import Hierarchy
from sfa.util.genitable import GeniTable
from sfa.util.config import *
from sfa.util.misc import *

class Auth:
    """
    Credential based authentication
    """

    def __init__(self, peer_cert = None, config = None ):
        self.peer_cert = peer_cert
        self.hierarchy = Hierarchy()
        if not config:
            self.config = Config()
        self.trusted_cert_list = TrustedRootList(self.config.get_trustedroots_dir()).get_list()


    def check(self, cred, operation):
        """
        Check the credential against the peer cert (callerGID included 
        in the credential matches the caller that is connected to the 
        HTTPS connection, check if the credential was signed by a 
        trusted cert and check if the credential is allowd to perform 
        the specified operation.    
        """
        self.client_cred = Credential(string = cred)
        self.client_gid = self.client_cred.get_gid_caller()
        self.object_gid = self.client_cred.get_gid_object()
        
        # make sure the client_gid is not blank
        if not self.client_gid:
            raise MissingCallerGID(self.client_cred.get_subject())

        # make sure the client_gid matches client's certificate
        peer_cert = self.peer_cert
        if not peer_cert.is_pubkey(self.client_gid.get_pubkey()):
            raise ConnectionKeyGIDMismatch(self.client_gid.get_subject())

        # make sure the client is allowed to perform the operation
        if operation:
            if not self.client_cred.can_perform(operation):
                raise InsufficientRights(operation)

        if self.trusted_cert_list:
            self.client_cred.verify_chain(self.trusted_cert_list)
            if self.client_gid:
                self.client_gid.verify_chain(self.trusted_cert_list)
            if self.object_gid:
                self.object_gid.verify_chain(self.trusted_cert_list)

        return True


    def verify_cred_is_me(self, credential):
        is_me = False 
        cred = Credential(string=credential)
        caller_gid = cred.get_gid_caller()
        caller_hrn = caller_gid.get_hrn()
        if caller_hrn != self.config.SFA_INTERFACE_HRN:
            raise GeniPermissionError(self.config.SFA_INTEFACE_HRN)

        return   
        
    def get_auth_info(self, auth_hrn):
        """
        Given an authority name, return the information for that authority.
        This is basically a stub that calls the hierarchy module.
        
        @param auth_hrn human readable name of authority  
        """

        return self.hierarchy.get_auth_info(auth_hrn)


    def veriry_auth_belongs_to_me(self, name):
        """
        Verify that an authority belongs to our hierarchy. 
        This is basically left up to the implementation of the hierarchy
        module. If the specified name does not belong, ane exception is 
        thrown indicating the caller should contact someone else.

        @param auth_name human readable name of authority
        """

        # get auth info will throw an exception if the authority doesnt exist
        self.get_auth_info(name)


    def verify_object_belongs_to_me(self, name):
        """
        Verify that an object belongs to our hierarchy. By extension,
        this implies that the authority that owns the object belongs
        to our hierarchy. If it does not an exception is thrown.
    
        @param name human readable name of object        
        """
        auth_name = self.get_authority(name)
        if not auth_name:
            auth_name = name 
        if name == self.config.SFA_INTERFACE_HRN:
            return
        self.verify_auth_belongs_to_me(auth_name) 
             
    def verify_auth_belongs_to_me(self, name):
        # get auth info will throw an exception if the authority doesnt exist
        self.get_auth_info(name) 


    def verify_object_permission(self, name):
        """
        Verify that the object gid that was specified in the credential
        allows permission to the object 'name'. This is done by a simple
        prefix test. For example, an object_gid for plc.arizona would 
        match the objects plc.arizona.slice1 and plc.arizona.
    
        @param name human readable name to test  
        """
        object_hrn = self.object_gid.get_hrn()
        if object_hrn == name:
            return
        if name.startswith(object_hrn + "."):
            return
        #if name.startswith(get_authority(name)):
            #return
    
        raise PermissionError(name)

    def determine_user_rights(self, src_cred, record):
        """
        Given a user credential and a record, determine what set of rights the
        user should have to that record.

        Src_cred can be None when obtaining a user credential, but should be
        set to a valid user credential when obtaining a slice or authority
        credential.

        This is intended to replace determine_rights() and
        verify_cancreate_credential()
        """

        type = record['type']
        if src_cred:
            cred_object_hrn = src_cred.get_gid_object().get_hrn()
        else:
            # supplying src_cred==None is only valid when obtaining user
            # credentials.
            #assert(type == "user")
            
            cred_object_hrn = None

        rl = RightList()

        if type=="slice":
            researchers = record.get("researcher", [])
            if (cred_object_hrn in researchers):
                rl.add("refresh")
                rl.add("embed")
                rl.add("bind")
                rl.add("control")
                rl.add("info")

        elif type == "authority":
            pis = record.get("pi", [])
            operators = record.get("operator", [])
            rl.add("authority,sa,ma")
            if (cred_object_hrn in pis):
                rl.add("sa")
            if (cred_object_hrn in operators):
                rl.add("ma")

        elif type == "user":
            rl.add("refresh")
            rl.add("resolve")
            rl.add("info")

        return rl

    def verify_cancreate_credential(self, src_cred, record):
        """
        Verify that a user can retrive a particular type of credential.
        For slices, the user must be on the researcher list. For SA and
        MA the user must be on the pi and operator lists respectively
        """

        type = record.get_type()
        cred_object_hrn = src_cred.get_gid_object().get_hrn()
        if cred_object_hrn in [self.config.SFA_REGISTRY_ROOT_AUTH]:
            return
        if type=="slice":
            researchers = record.get("researcher", [])
            if not (cred_object_hrn in researchers):
                raise PermissionError(cred_object_hrn + " is not in researcher list for " + record.get_name())
        elif type == "sa":
            pis = record.get("pi", [])
            if not (cred_object_hrn in pis):
                raise PermissionError(cred_object_hrn + " is not in pi list for " + record.get_name())
        elif type == "ma":
            operators = record.get("operator", [])
            if not (cred_object_hrn in operators):
                raise PermissionError(cred_object_hrn + " is not in operator list for " + record.get_name())

    def get_authority(self, hrn):
        return get_authority(hrn)
